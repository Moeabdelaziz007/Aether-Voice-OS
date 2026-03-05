#!/usr/bin/env python3
"""
Aether Voice OS — Dynamic Parameter Controller
=============================================

Interactive controller for adjusting audio parameters during live testing.
Allows real-time tuning of AEC, VAD, and other audio processing parameters.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from core.infra.config import AudioConfig

logger = logging.getLogger("param_controller")


# ANSI Color Codes
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


@dataclass
class ParameterPreset:
    """Predefined parameter configurations for different scenarios."""

    name: str
    description: str
    parameters: Dict[str, float]


class DynamicParameterController:
    """Controller for dynamic parameter adjustment during live testing."""

    def __init__(self, audio_config: AudioConfig):
        self.config = audio_config
        self.callbacks: List[Callable[[str, float], None]] = []
        self.running = False
        self.active_preset = "default"

        # Define parameter ranges and presets
        self.parameters = {
            # AEC Parameters
            "aec_step_size": {
                "value": self.config.aec_step_size,
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
                "description": "AEC learning rate",
            },
            "aec_filter_length_ms": {
                "value": self.config.aec_filter_length_ms,
                "min": 50.0,
                "max": 300.0,
                "step": 10.0,
                "description": "AEC filter length",
            },
            "aec_convergence_threshold_db": {
                "value": self.config.aec_convergence_threshold_db,
                "min": 5.0,
                "max": 25.0,
                "step": 1.0,
                "description": "AEC convergence threshold",
            },
            # VAD Parameters
            "vad_energy_threshold": {
                "value": self.config.vad_energy_threshold,
                "min": 0.001,
                "max": 0.1,
                "step": 0.005,
                "description": "VAD energy threshold",
            },
            "vad_soft_threshold_multiplier": {
                "value": self.config.vad_soft_threshold_multiplier,
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
                "description": "VAD soft threshold multiplier",
            },
            # Jitter Buffer Parameters
            "jitter_buffer_target_ms": {
                "value": self.config.jitter_buffer_target_ms,
                "min": 20.0,
                "max": 150.0,
                "step": 10.0,
                "description": "Jitter buffer target",
            },
            # Timing Parameters
            "mute_delay_samples": {
                "value": float(self.config.mute_delay_samples),
                "min": 100.0,
                "max": 2000.0,
                "step": 100.0,
                "description": "Mute delay samples",
            },
            "unmute_delay_samples": {
                "value": float(self.config.unmute_delay_samples),
                "min": 100.0,
                "max": 3000.0,
                "step": 100.0,
                "description": "Unmute delay samples",
            },
        }

        # Define presets
        self.presets = {
            "default": ParameterPreset(
                "default",
                "Balanced settings for general use",
                {
                    "aec_step_size": 0.5,
                    "aec_filter_length_ms": 100.0,
                    "aec_convergence_threshold_db": 15.0,
                    "vad_energy_threshold": 0.02,
                    "vad_soft_threshold_multiplier": 0.7,
                    "jitter_buffer_target_ms": 60.0,
                    "mute_delay_samples": 800.0,
                    "unmute_delay_samples": 1200.0,
                },
            ),
            "low_latency": ParameterPreset(
                "low_latency",
                "Optimized for minimum latency",
                {
                    "aec_step_size": 0.8,
                    "aec_filter_length_ms": 50.0,
                    "aec_convergence_threshold_db": 10.0,
                    "vad_energy_threshold": 0.01,
                    "vad_soft_threshold_multiplier": 0.5,
                    "jitter_buffer_target_ms": 30.0,
                    "mute_delay_samples": 400.0,
                    "unmute_delay_samples": 600.0,
                },
            ),
            "high_quality": ParameterPreset(
                "high_quality",
                "Optimized for maximum audio quality",
                {
                    "aec_step_size": 0.3,
                    "aec_filter_length_ms": 200.0,
                    "aec_convergence_threshold_db": 20.0,
                    "vad_energy_threshold": 0.03,
                    "vad_soft_threshold_multiplier": 0.8,
                    "jitter_buffer_target_ms": 100.0,
                    "mute_delay_samples": 1200.0,
                    "unmute_delay_samples": 1800.0,
                },
            ),
            "noisy_environment": ParameterPreset(
                "noisy_environment",
                "Robust settings for noisy environments",
                {
                    "aec_step_size": 0.4,
                    "aec_filter_length_ms": 150.0,
                    "aec_convergence_threshold_db": 12.0,
                    "vad_energy_threshold": 0.05,
                    "vad_soft_threshold_multiplier": 0.9,
                    "jitter_buffer_target_ms": 80.0,
                    "mute_delay_samples": 1000.0,
                    "unmute_delay_samples": 1500.0,
                },
            ),
        }

    def add_callback(self, callback: Callable[[str, float], None]):
        """Add a callback function to be notified of parameter changes."""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[str, float], None]):
        """Remove a callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def set_parameter(self, param_name: str, value: float):
        """Set a parameter value and notify callbacks."""
        if param_name not in self.parameters:
            raise ValueError(f"Unknown parameter: {param_name}")

        # Clamp value to valid range
        param_info = self.parameters[param_name]
        value = max(param_info["min"], min(param_info["max"], value))

        # Update parameter
        self.parameters[param_name]["value"] = value

        # Update config
        if hasattr(self.config, param_name):
            setattr(self.config, param_name, value)

        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(param_name, value)
            except Exception as e:
                logger.error(f"Callback error: {e}")

        logger.info(f"Parameter '{param_name}' set to {value}")

    def get_parameter(self, param_name: str) -> float:
        """Get current parameter value."""
        if param_name not in self.parameters:
            raise ValueError(f"Unknown parameter: {param_name}")
        return self.parameters[param_name]["value"]

    def apply_preset(self, preset_name: str):
        """Apply a predefined parameter preset."""
        if preset_name not in self.presets:
            raise ValueError(f"Unknown preset: {preset_name}")

        preset = self.presets[preset_name]
        self.active_preset = preset_name

        for param_name, value in preset.parameters.items():
            self.set_parameter(param_name, value)

        logger.info(f"Applied preset: {preset_name} - {preset.description}")

    def get_current_state(self) -> Dict[str, Any]:
        """Get current parameter values."""
        return {
            param_name: param_info["value"]
            for param_name, param_info in self.parameters.items()
        }

    def save_preset(self, filename: str):
        """Save current parameters as a preset file."""
        state = self.get_current_state()
        preset_data = {
            "name": "custom",
            "description": "Custom user preset",
            "parameters": state,
        }

        with open(filename, "w") as f:
            json.dump(preset_data, f, indent=2)

        logger.info(f"Preset saved to {filename}")

    def load_preset(self, filename: str):
        """Load parameters from a preset file."""
        try:
            with open(filename, "r") as f:
                preset_data = json.load(f)

            for param_name, value in preset_data["parameters"].items():
                if param_name in self.parameters:
                    self.set_parameter(param_name, value)

            logger.info(f"Preset loaded from {filename}")
        except Exception as e:
            logger.error(f"Failed to load preset: {e}")
            raise

    def interactive_control(self):
        """Start interactive parameter control via keyboard input."""
        print(
            f"\n{Colors.BOLD}{Colors.CYAN}Dynamic Parameter Controller Started{Colors.RESET}"
        )
        print("Commands:")
        print("  [1-8] Adjust parameters")
        print("  [p] Apply preset")
        print("  [s] Show current values")
        print("  [q] Quit controller")
        print()

        while True:
            try:
                self._show_menu()
                choice = input("Enter command: ").strip().lower()

                if choice == "q":
                    break
                elif choice == "s":
                    self._show_current_values()
                elif choice == "p":
                    self._apply_preset_interactive()
                elif choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    param_keys = list(self.parameters.keys())
                    if int(choice) <= len(param_keys):
                        param_name = param_keys[int(choice) - 1]
                        self._adjust_parameter(param_name)
                else:
                    print(f"{Colors.RED}Invalid command{Colors.RESET}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def _show_menu(self):
        """Display parameter adjustment menu."""
        print(f"\n{Colors.BOLD}Adjustable Parameters:{Colors.RESET}")
        param_list = list(self.parameters.items())

        for i, (param_name, param_info) in enumerate(param_list[:8], 1):
            current_value = param_info["value"]
            print(
                f"  {i}. {param_name}: {current_value:.2f} ({param_info['description']})"
            )

        print()

    def _show_current_values(self):
        """Display all current parameter values."""
        print(f"\n{Colors.BOLD}Current Parameter Values:{Colors.RESET}")
        for param_name, param_info in self.parameters.items():
            value = param_info["value"]
            min_val = param_info["min"]
            max_val = param_info["max"]
            print(
                f"  {param_name:25s}: {value:8.2f} (range: {min_val:.2f} - {max_val:.2f})"
            )
        print()

    def _apply_preset_interactive(self):
        """Interactively apply a preset."""
        print(f"\n{Colors.BOLD}Available Presets:{Colors.RESET}")
        preset_list = list(self.presets.items())

        for i, (preset_name, preset) in enumerate(preset_list, 1):
            active_marker = " (*)" if preset_name == self.active_preset else ""
            print(f"  {i}. {preset_name}: {preset.description}{active_marker}")

        try:
            choice = int(input("Select preset (1-{}): ".format(len(preset_list))))
            if 1 <= choice <= len(preset_list):
                preset_name = preset_list[choice - 1][0]
                self.apply_preset(preset_name)
            else:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error applying preset: {e}{Colors.RESET}")

    def _adjust_parameter(self, param_name: str):
        """Interactively adjust a single parameter."""
        param_info = self.parameters[param_name]
        current_value = param_info["value"]
        min_val = param_info["min"]
        max_val = param_info["max"]
        step = param_info["step"]

        print(f"\nAdjusting {Colors.BOLD}{param_name}{Colors.RESET}")
        print(f"Current value: {current_value:.2f}")
        print(f"Range: {min_val:.2f} - {max_val:.2f}")
        print(f"Step: {step:.2f}")
        print("Commands: [+][-][value] or [enter] to cancel")

        try:
            user_input = input("New value: ").strip()

            if not user_input:
                return  # Cancel

            if user_input == "+":
                new_value = current_value + step
            elif user_input == "-":
                new_value = current_value - step
            else:
                new_value = float(user_input)

            self.set_parameter(param_name, new_value)
            print(f"{Colors.GREEN}Set {param_name} = {new_value:.2f}{Colors.RESET}")

        except ValueError:
            print(f"{Colors.RED}Invalid number format{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error setting parameter: {e}{Colors.RESET}")


# Example usage and integration
def create_parameter_controller(
    audio_config: AudioConfig,
) -> DynamicParameterController:
    """Factory function to create a parameter controller."""
    return DynamicParameterController(audio_config)


def integrate_with_benchmark(
    benchmark_instance, controller: DynamicParameterController
):
    """Integrate parameter controller with benchmark instance."""

    def parameter_callback(param_name: str, value: float):
        # Forward parameter changes to benchmark
        if hasattr(benchmark_instance, "update_parameters"):
            benchmark_instance.update_parameters(**{param_name: value})

    controller.add_callback(parameter_callback)
    return controller


if __name__ == "__main__":
    # Example usage
    from core.infra.config import AudioConfig

    # Create audio config
    config = AudioConfig()

    # Create controller
    controller = DynamicParameterController(config)

    # Start interactive control
    controller.interactive_control()
