import pytest
import torch

from src.domains.audio.dsp.audio import load_waveform
from src.domains.audio.dsp.augmentation import AudioAugmenter
from src.utils.env import BASE_DIR


@pytest.fixture
def sample_waveform() -> torch.Tensor:
    return load_waveform(
        BASE_DIR.joinpath("tests/data/test.wav").as_posix(),
        sample_rate=16000,
    )


def test_audio_augmenter_no_augmentations():
    with pytest.raises(
        ValueError,
        match=(
            "Invalid initialization: No augmentations selected. At least one "
            "augmentation method should be enabled."
        ),
    ):
        AudioAugmenter(
            sample_rate=16000,
            use_sox_effects=False,
            use_room_reverberation=False,
            use_background_noise=False,
        )


def test_audio_augmenter_initialization():
    augmenter = AudioAugmenter(
        sample_rate=16000,
        use_sox_effects=True,
        use_room_reverberation=True,
        use_background_noise=True,
    )
    assert augmenter.sample_rate == 16000
    assert augmenter.use_sox_effects
    assert augmenter.use_room_reverberation
    assert augmenter.use_background_noise


def test_audio_augmenter_with_sox_effects(sample_waveform: torch.Tensor):
    augmenter = AudioAugmenter(
        sample_rate=16000,
        use_sox_effects=True,
        max_pitch_shift=2,
        max_tempo_change=0.1,
    )
    augmented_waveform = augmenter(sample_waveform)
    assert isinstance(
        augmented_waveform, torch.Tensor
    ), "Returned augmented waveform is not a tensor"


def test_audio_augmenter_with_room_reverberation(
    sample_waveform: torch.Tensor,
):
    augmenter = AudioAugmenter(sample_rate=16000, use_room_reverberation=True)
    augmented_waveform = augmenter(sample_waveform)
    assert isinstance(
        augmented_waveform, torch.Tensor
    ), "Returned augmented waveform is not a tensor"


def test_audio_augmenter_with_background_noise(sample_waveform: torch.Tensor):
    augmenter = AudioAugmenter(
        sample_rate=16000, use_background_noise=True, snr_dbs=[0, 10, 20]
    )
    augmented_waveform = augmenter(sample_waveform)
    assert isinstance(
        augmented_waveform, torch.Tensor
    ), "Returned augmented waveform is not a tensor"
