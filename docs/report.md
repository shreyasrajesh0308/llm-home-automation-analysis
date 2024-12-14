---
layout: default
title: Project Report
---

# Table of Contents
* Abstract
* [Introduction](#1-introduction)
* [Related Work](#2-related-work)
* [Technical Approach](#3-technical-approach)
* [Evaluation and Results](#4-evaluation-and-results)
* [Discussion and Conclusions](#5-discussion-and-conclusions)
* [References](#6-references)

# Abstract

This project explores the integration of large language models (LLMs) into smart home automation systems, accessing the LLM's ability to understand and execute complex instructions regarding home automation, and evaluate how different factors, such as model size and levels of quantization, affect the performance and latency of the LLM. We evaluate various LLMs across a collection of tasks with differing complexities. Our findings reveal that open-source models can achieve competitive performance to proprietary models, and that quantization can significantly reduce the latency of the LLM. We propose potential home automation choice such as using heavily quantized models with larger parameter counts for better performance under same computational constraints.
# 1. Introduction

This section should cover the following items:
## Motivation & Objective

Smart home technologies have transformed daily life by automating everyday home tasks. However, previous Command-and-control interfaces has many limitations. First, it requires users to use specific keywords or phrases. For example, it can handle "Turn on the kitchen light" but fails with "Can you brighten the kitchen for me?" which is a more natural way to express the request but does not follow the specific keywords. Second, it lacks flexibility in handling multi-step or contextual queries. For example, users can't easily say "Turn on all lights except the living room" which requires reasoning about the setting of the house. Third, it fails when commands are ambiguous or require reasoning (e.g., "Turn on the heat if it's cold outside" needs to infer the external conditions and do reasoning). Fourth, it can't handle multi-turn conversations. For example, if the user says "Turn on the light" and then follows up with "Wait, not the living room light", the system needs to turn off the living room light and then turn on the correct light, which needs multi-turn conversation understanding.

Reecently, LLMs have shown great potential in handling complex instructions and multi-turn conversations. And many smart home devices such as Google Home, Amazon Echo, and Apple HomeKit have already integrated LLMs into their systems. But these systems are still doing api calls to really large models, which mean raise privacy concerns and waste computational resources. This project aims to explore whether smaller, open-source LLMs can serve as a cost-efficient and resource-friendly alternative to larger proprietary models, while maintaining high performance.

## State of the Art & Its Limitations: 
Most of the existing smart home devices are using large proprietary models, which are not open-source and raise privacy concerns. Moreover, these use models with huge number of parameters (often > 100B), which are not friendly to resource-constrained devices. We argue that to handle everyday home automation tasks, we don't need to use really large proprietary models, and open-source models can achieve competitive performance to proprietary models while being more privacy-friendly.
## Novelty & Rationale: 
The novelty of this project is that we innovatively apply open-source LLMs to a simulated smart home environment, which can be used to generate large-scale datasets with diverse and complex home automation tasks. Further, by using the simulated environments and using LLMs to generate human-like commands, we can evaluate the performance of the LLM in a more realistic and challenging way. We also novelly generated various sets of datasets with different complexities to evaluate the performance of the LLM under different levels of complexity of tasks. The rationale is that the majority of everyday home automation tasks are not complex, and we can use simpler models to handle them. If the task is complex, we can always yields to use more complex models to handle it.
## Potential Impact: 
The success of this project could:
- Create a new choice for smart home devices to use smaller, open-source LLMs, which are more privacy-friendly and friendly to resource-constrained devices.
- Lower the barrier for advanced smart home automation by making it accessible to broader markets.
- Improve the flexibility and responsiveness of IoT systems.
## Challenges:
The main challenge is that our simulated environment still cannot cover all the real-world scenarios. In real-world, there are many unpredictable factors that can affect the user's behavior and the environment, which are not covered in our simulated environment. Also, it is difficult to actually evalute how good the LLM's command generation is, since we cannot directly apply the LLM to real-world scenarios and observe the real-world results.
## Requirements for Success: 
- We need to build a simulated environment that can simulate the real-world scenarios.      
- We need to generate a large-scale dataset with diverse and complex home automation tasks.
- We need to evaluate the performance of the LLM using robust evaluation metrics, including accuracy, latency, memory usage, and more.
## Metrics of Success: 
The metrics of success will be the success evaluation of the LLM's performance on the generated datasets, including the accuracy of the LLM's command generation, the latency of the LLM's command execution, the memory usage of the LLM's command execution, and more.

# 2. Related Work

# 3. Technical Approach
## Home Simulation
To generate the diverse and complex home automation tasks, we build a simulated home environment, which can simulate the real-world scenarios. We divide the simulation into different levels: devices, rooms, and the whole house. We also simulate the user's commands and the environment's states to generate the datasets.
### Devices
Devices are the fundamental units in our simulated smart home environment. Each device supports various functions and states, such as turning on/off, adjusting settings, or changing modes. Here is the example of the device class:
```
Device: Living Room Light
    - Action: turn_on
      Description: Turns the device on.

    - Action: turn_off
      Description: Turns the device off.

    - Action: set_status
      Description: Sets the status of the device.

    - Action: get_status
      Description: Retrieves the current status of the device.

    - Action: set_brightness
      Description: Adjusts the brightness of the light.
      Parameters:
        - brightness (int): Brightness level, range 0-100.
    - Action: set_color_temp
      Description: Changes the color temperature of the light.
      Parameters:  
        - color_temp (int): Color temperature in Kelvin, range 2700-6500.
```
### Rooms
Rooms aggregate multiple devices, forming a cohesive functional unit. For instance:
```
Room: Living Room
    - Devices:
        - Living Room Light
        - Living Room AC
        - Living Room TV
```
### House
Houses represent the highest hierarchical unit in the simulation, composed of multiple rooms. The house simulation allows for dynamic configurations, enabling diverse scenarios for model evaluation. For example, a house can have three rooms: Living Room, Kitchen, and Bedroom, each containing specific devices.

### Command
Commands are generated based on the house and device configurations. They are categorized by complexity:

- Simple Commands: Single-step actions, e.g., "Set the living room light to warm white."
- Composite Commands: Multi-step actions, e.g., "Turn off the bedroom light and AC."
- Complex Commands: Context-dependent actions requiring reasoning, e.g., "If no one is in the room, turn off all devices."

These commands are further converted into natural language for evaluation.


# 4. Evaluation and Results

# 5. Discussion and Conclusions

# 6. References
