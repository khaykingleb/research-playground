"""Augmentations for digital signals."""

import math
import random
import typing as tp

import torch
import torch.nn.functional as F  # NOQA
import torchaudio
from omegaconf import DictConfig, OmegaConf

from ... import cfg

CONFIG = OmegaConf.load(cfg.BASE_PATH / "configs/asr/quartznet.yaml")

rir, sample_rate = torchaudio.load(
    torchaudio.utils.download_asset(
        "tutorial-assets/Lab41-SRI-VOiCES-rm1-impulse-mc01-stu-clo-8000hz.wav"
    )
)
rir = torchaudio.functional.resample(
    rir,
    sample_rate,
    CONFIG.preprocess.sr,
    lowpass_filter_width=6,
)
rir = rir[:, int(CONFIG.preprocess.sr * 1.01) : int(CONFIG.preprocess.sr * 1.3)]
rir = rir / torch.norm(rir, p=2)
RIR = torch.flip(rir, [1])

NOISE, sample_rate = torchaudio.load(
    torchaudio.utils.download_asset(
        "tutorial-assets/Lab41-SRI-VOiCES-rm1-babb-mc01-stu-clo-8000hz.wav"
    )
)
NOISE = torchaudio.functional.resample(
    NOISE,
    sample_rate,
    CONFIG.preprocess.sr,
    lowpass_filter_width=6,
)


class AudioAugmenter:
    """Augments digital signals."""

    def __init__(self: "AudioAugmenter", audio_config: DictConfig) -> None:
        """Constructor.

        Args:
            audio_config (DictConfig): Audio preprocessing part of the configuration file.
        """
        self.audio_config = audio_config

    def __apply_sox_effect(
        self: "AudioAugmenter",
        audio: torch.Tensor,
        sample_rate: int,
    ) -> tp.Tuple[torch.Tensor, int]:
        """Apply SOX effect to the digital signal.

        Args:
            audio (Tensor): Audio signal of shape (1, n_length).
            sample_rate (int): Original sampling rate.

        Returns:
            Tuple: (augmented audio signal, sample_rate).
        """
        if self.audio_config.use_sox_effects:
            effects_to_choose = [
                ["pitch", str(self.audio_config.effects.pitch)],
                [
                    "tempo",
                    str(1 + self.audio_config.effects.tempo * random.uniform(-1, 1)),
                ],
                [
                    "speed",
                    str(1 + self.audio_config.effects.speed * random.uniform(-1, 1)),
                ],
                ["reverb", "-w"],
            ]
            return torchaudio.sox_effects.apply_effects_tensor(
                audio,
                sample_rate,
                [random.choice(effects_to_choose), ["rate", str(sample_rate)]],
                channels_first=True,
            )
        return audio

    def __simulate_room_reverberation(
        self: "AudioAugmenter",
        audio: torch.Tensor,
    ) -> torch.Tensor:
        """Use Room Impulse Response (RIR) to make speech sound as though it has been uttered in a conference room.

        Args:
            audio (Tensor): Audio signal of shape (1, n_length).

        Returns:
            Augmented audio signal.
        """
        if self.audio_config.use_room_reverberation:
            audio = F.pad(audio, (RIR.shape[1] - 1, 0))
            return F.conv1d(audio[None, ...], RIR[None, ...])[0]
        return audio

    def __add_background_noise(
        self: "AudioAugmenter",
        audio: torch.Tensor,
    ) -> torch.Tensor:
        """Add background noise to the digital signal.

        Args:
            audio (Tensor): Audio signal of shape (1, n_length).

        Returns:
            Tensor: Audio signal with noise.
        """
        if self.audio_config.use_background_noise:
            n_repeat = math.ceil(audio.shape[1] / NOISE.shape[1])
            noise = NOISE.repeat([1, n_repeat])
            noise = noise[:, : audio.shape[1]]
            audio_rms = audio.norm(p=2)
            noise_rms = noise.norm(p=2)
            noisy_audios = []
            for snr_db in self.audio_config.snr_dbs:
                snr = 10 ** (snr_db / 20)
                snr_ratio = snr * noise_rms / audio_rms
                noisy_audios.append((snr_ratio * audio + noise) / 2)
            return random.choice(noisy_audios)
        return audio

    def __call__(
        self: "AudioAugmenter",
        audio: torch.Tensor,
        /,
        *,
        sample_rate: int,
    ) -> torch.Tensor:
        """Augments digital signal according to the configuration file.

        Args:
            audio (Tensor): Audio signal of shape (1, n_length).
            sample_rate (int): Original sampling rate.

        Returns:
            Tensor: Augmented audio signal.
        """
        audio_augmented = {
            "sox_effect": self.__apply_sox_effect(audio, sample_rate)[0],
            "room_reverberation": self.__simulate_room_reverberation(audio),
            "background_noise": self.__add_background_noise(audio),
            "none": audio,
        }
        return audio_augmented[random.choice(list(audio_augmented.keys()))]
