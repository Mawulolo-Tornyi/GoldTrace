from src.hardware_feature_inference import (
    is_summary_packet,
    predict_audio_summary,
    predict_vibration_summary,
)


def test_summary_packet_detection():
    packet = {
        "precomputed_features": {
            "audio_rms": 0.01,
            "audio_peak": 0.03,
            "audio_zero_crossing_rate": 0.1,
            "vibration_rms": 0.02,
            "vibration_peak": 0.05,
        },
        "audio_samples": None,
        "vibration_samples": None,
    }


    assert (
        is_summary_packet(
            packet
        )
        is True
    )


def test_raw_packet_is_not_summary_packet():
    packet = {
        "precomputed_features": {
            "audio_rms": 0.01,
        },
        "audio_samples": [
            0.1,
            0.2,
        ],
    }


    assert (
        is_summary_packet(
            packet
        )
        is False
    )


def test_audio_without_baseline_is_unknown():
    result = predict_audio_summary(
        {
            "audio_rms": 0.02,
            "audio_peak": 0.07,
            "audio_zero_crossing_rate": 0.08,
        },
        None,
    )


    assert (
        result["audio_class"]
        ==
        "UNKNOWN_AUDIO"
    )


    assert (
        result["baseline_ready"]
        is False
    )


    assert (
        result["confidence"]
        <= 0.60
    )


def test_audio_large_baseline_change_marks_machine_like():
    result = predict_audio_summary(
        {
            "audio_rms": 0.05,
            "audio_peak": 0.11,
            "audio_zero_crossing_rate": 0.06,
        },
        {
            "audio_rms": 0.01,
        },
    )


    assert (
        result[
            "machine_probability"
        ]
        >= 0.65
    )


    assert (
        result["audio_class"]
        ==
        "UNKNOWN_MACHINE"
    )


    assert (
        result["confidence"]
        <= 0.60
    )


def test_vibration_without_baseline_is_unknown():
    result = predict_vibration_summary(
        {
            "vibration_rms": 0.03,
            "vibration_peak": 0.08,
        },
        None,
    )


    assert (
        result["vibration_class"]
        ==
        "UNKNOWN_VIBRATION"
    )


    assert (
        result["baseline_ready"]
        is False
    )


def test_vibration_large_baseline_change_marks_machinery_like():
    result = predict_vibration_summary(
        {
            "vibration_rms": 0.06,
            "vibration_peak": 0.12,
        },
        {
            "vibration_rms": 0.01,
        },
    )


    assert (
        result[
            "machinery_probability"
        ]
        >= 0.65
    )


    assert (
        result["vibration_class"]
        ==
        "HEAVY_MACHINERY"
    )


    assert (
        result["confidence"]
        <= 0.60
    )
