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

## Motivation & Objective

Smart home technologies have transformed daily life by automating everyday home tasks and the market is growing rapidly [4]. However, previous Command-and-control interfaces has many limitations. First, it requires users to use specific keywords or phrases. For example, it can handle "Turn on the kitchen light" but fails with "Can you brighten the kitchen for me?" which is a more natural way to express the request but does not follow the specific keywords. Second, it lacks flexibility in handling multi-step or contextual queries. For example, users can't easily say "Turn on all lights except the living room" which requires reasoning about the setting of the house. Third, it fails when commands are ambiguous or require reasoning (e.g., "Turn on the heat if it's cold outside" needs to infer the external conditions and do reasoning). Fourth, it can't handle multi-turn conversations. For example, if the user says "Turn on the light" and then follows up with "Wait, not the living room light", the system needs to turn off the living room light and then turn on the correct light, which needs multi-turn conversation understanding.

Reecently, LLMs have shown great potential in handling complex instructions and multi-turn conversations[1][2][3]. And many smart home devices such as Google Home, Amazon Echo, and Apple HomeKit have already integrated LLMs into their systems[5]. But these systems are still doing api calls to really large models, which mean raise privacy concerns and waste computational resources. This project aims to explore whether smaller, open-source LLMs can serve as a cost-efficient and resource-friendly alternative to larger proprietary models, while maintaining high performance.

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

- Simple Commands: Single-step actions, e.g., "Set the living room light to warm white.
  Example 1: "Change living room light to 10% brightness"
  Example 2: "Set living room light to warm white"
- Composite Commands: Multi-step actions, e.g., "Turn off the bedroom light and AC."
  Example 1: "Turn off the bedroom light and the bedroom AC"
  Example 2: "Set bedroom AC temperature to 23 and switch to cooling mode."
- Complex Commands: Context-dependent actions requiring reasoning, e.g., "If no one is in the room, turn off all devices."
  Example 1: "If no one is in the bedroom, turn off all devices."
  Example 2: "If bedroom is occupied, set light to warm white and 50% brightness."

These commands are further converted into natural language for evaluation.

## Other Design Tricks
### Structured Output and Fast Generation
LLMs are fundamentally next token predictors, however, for home automation tasks, we need precise outputs since APIs need to be called. A tiny error in the output format can lead to a huge error in the API call. Therefore, the output of the LLM needs to follow specific structures.

To achieve this, we are using outlines to make LLMs generate structured output (json-like)[7]. Outlines actually provide a way to control and "guide" the LLM to generate the output in a specific format, thus, if will have no harm to the performance of the LLM, in some cases, it can even improve the performance of the LLM due to the guidance provided by the provided structure. 

### Result Comparison
Our commands can be open-ended. For example, the command "I feel cold" can be interpreted as "Turn off the AC if it's in cooling mode" or "Increase the AC temperature to 25 degrees". Therefore, we cannot directly compare the exact match of the output between the LLM and the ground truth. Our tiny workaround is that we are using another LLM to compare and evaluate the generated commands by the LLM and the ground truth. This is a bit hacky as we are not sure whether the LLM evaluator is accurate enough. One potential future improvements is to make the LLM agents more interactive, so that it can directly call the API and compare the real-world results.

### Prompt Engineering
Prompt engineering is a crucial part of this project. We need to design a prompt that provide the LLM with existing API functions, and show LLM examples of how to interpret the user's commands and generate the corresponding API calls. We did manual prompt engineering with CoT for the first version of our project[6], but we want to explore some joint optimization methods for the prompt and the model. We also realize that the same prompt may not be optimal for all models, and we want to explore some prompt optimization methods for different models.


# 4. Evaluation and Results
## Model Used
The following models are used in our experiments:
- GPT 4o Mini
- Qwen2.5 32B Quantized Q5
- Llama 3.1 8B Instruct fp32
- Llama 3.2 1B Instruct fp16
## Evaluation results
**Accuracy**

| Model             | Simple       | Conjugate    | Complex      |
|-------------------|--------------|--------------|--------------|
| GPT-4o-mini      | 0.960 ± 0.02 | 0.950 ± 0.03 | 0.890 ± 0.02 |
| Qwen 32B         | 0.980 ± 0.01 | 0.930 ± 0.02 | 0.730 ± 0.02 |
| Llama 3.1 (8B)   | 0.933 ± 0.01 | 0.630 ± 0.02 | 0.200 ± 0.03 |
| Llama 3.2 (1B)   | 0.570 ± 0.03 | 0.220 ± 0.02 | 0.000        |

**Latency and Resource Usage**

| Model             | Latency (s)   | Memory Requirements | Hardware            | Cost ($/mil tokens) |
|-------------------|---------------|----------------------|---------------------|---------------------|
| GPT-4o-mini      | 3.45 ± 0.5    | NA                   | API                 | 0.6                 |
| Qwen 32B         | 6.77 ± 0.33   | 23.74 GB             | Server-grade GPU    | NA                  |
| Llama-3.1 8B     | 7.57 ± 0.4    | 32 GB                | Server-grade GPU    | NA                  |
| Llama-3.2 1B     | 1.45 ± 0.5    | 2.48 GB              | Edge devices        | NA                  |


# 5. Discussion and Conclusions
Through our experiments, we find that open-source models can achieve competitive performance to proprietary models, and that quantization can significantly reduce the latency of the LLM. We propose potential home automation choice such as using heavily quantized models with larger parameter counts for better performance under same computational constraints.
## Proposed Solutions
- For basic home automation tasks, a lightweight 1b model is sufficient.
- For complex home automation tasks, a larger model is needed. It is recommended to use a larger model with quantization rather than a smaller model without quantization.
## Future Work
- Hybrid Approach: Leveraging both open-source and closed-source models through a routing mechanism[9].
- Prompt Engineering: Exploring joint optimization methods for prompt and model.
- Model Evaluation: Evaluating the performance of the LLM in a more interactive and challenging way.
# 6. References

[1] Achiam, Josh, et al. "GPT-4 Technical Report." arXiv preprint arXiv:2303.08774 (2023).

[2] Dubey, Abhimanyu, et al. "The Llama 3 Herd of Models." arXiv preprint arXiv:2407.21783 (2024).

[3] Bai, Jinze, et al. "Qwen Technical Report." arXiv preprint arXiv:2309.16609 (2023).

[4] Statista. "Smart Home Market Worldwide." [Link](https://www.statista.com/outlook/cmo/smart-home/worldwide)

[5] AWS Blog. "Emerging Architecture Patterns for Integrating IoT and Generative AI on AWS." [Link](https://aws.amazon.com/blogs/iot/emerging-architecture-patterns-for-integrating-iot-and-generative-ai-on-aws/)

[6] Wei, Jason, et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." Advances in Neural Information Processing Systems 35 (2022): 24824-24837.

[7] GitHub. "Outlines." [Link](https://github.com/dottxt-ai/outlines)

[8] Khattab, Omar, et al. "Dspy: Compiling Declarative Language Model Calls into Self-Improving Pipelines." arXiv preprint arXiv:2310.03714 (2023).

[9] Ong, Isaac, et al. "RouteLLM: Learning to Route LLMs with Preference Data." arXiv preprint arXiv:2406.18665 (2024).

[10] Patil, Shishir G., et al. "Gorilla: Large Language Model Connected with Massive APIs." arXiv preprint arXiv:2305.15334 (2023).

[11] Zhang, Tianjun, et al. "RAFT: Adapting Language Model to Domain Specific RAG." arXiv preprint arXiv:2403.10131 (2024).

