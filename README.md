# LLM Home Automation Analysis

A comprehensive analysis of Local Large Language Models (LLMs) for home automation applications, focusing on performance tradeoffs across different model sizes and deployment strategies.

## Authors
- Shreyas Rajesh (shreyasrajesh38@g.ucla.edu)
- Chenda Duan

## Project Overview

### Primary Goal
To analyze and evaluate the performance of Large Language Models (LLMs) in home automation applications, focusing on the relationships between instruction complexity, model size, system resources, and execution performance.

### Primary Research Questions
Understanding Tradeoffs between model size, performance, query complexity and cost:
1. How do different classes of LLMs perform in home automation contexts?
2. What are the key tradeoffs between model sizes and deployment options?
3. How does the complexity of instruction decide which scale of model to be used? 
4. Possibly exploration into Routing calls based on the level of complexity of the instruction. (Explorations along the lines of https://lmsys.org/blog/2024-07-01-routellm/)

## Model Categories

### 1. Small Language Models (Embedded Deployment)
- **Size Range**: 1-3B parameters
- **Deployment**: Direct on embedded device (Jetson Nano)
- **Examples**: LLama3.2 - 1B and 3B Variants, Heavily Quantized 7B models

### 2. Medium-Size Open Source Models (Local Server)
- **Size Range**: 7-70B parameters
- **Deployment**: Local production server (A6000, A100, H100)
- **Examples**: Llama-3.1 7B, 70B, Mistral etc. Other MoE models as well

### 3. Large Closed-Source Models (API Access)
- **Size Range**: 70B+ parameters
- **Deployment**: Cloud API calls
- **Examples**: GPT4, Claude, Grok

## Analysis Vectors

### 1. Performance Metrics

#### Command Understanding and Accuracy
- Simple commands (single action)
- Composite commands (multiple actions)
- Complex contextual commands (Inferring command based on user want)
- Error rate analysis

#### Latency Analysis
- Response time measurement
- Latency variance
- Network latency and reliability (for API calls)

#### Instruction Complexity Handling
- Instruction complexity supported with high accuracy
- Degradation patterns with increasing complexity
- Reasoning capabilities based on user inputs

### 2. Operational Considerations

#### Cost Analysis
- Hardware/Deployment costs (embedded/server)
- API costs (per-query pricing)

#### Security and Privacy Assessment
- Security Implications especially for cloud based closed source models

## Expected Outcomes

### 1. Quantitative Analysis
- Performance vs. Cost curves for each model category
- Accuracy vs. Instruction complexity relationships
- Latency analysis for the analyzed model classes

### 2. Decision Framework
- Model selection guidelines based on use case
- Deployment architecture recommendations
- Cost-benefit analysis framework
- Possible study on using a mix of all kinds of models guided by a router

## Project Requirements
1. Jetson-Nano/other type of embedding platform
2. Access to open source home automation systems
3. Home automation test-bed (lights, smart plugs etc.)
4. Server Grade GPUs to host mid-size models
5. API access to SOTA models

## Implementation Steps
1. Analyze the API of home automation system and use Large closed models to generate a training/evaluation set (Command and Instruction pairs)
2. Zero-shot evaluating the small and mid-sized language models
   - If performance is bad (we expected this to happen with smaller models), considering finetuning
3. Evaluating the accuracy of different models
4. Deploy the smaller model/mid sized model and test latency/costs
5. Ablation studies (Instruction complexity handling analysis, Security Assessment)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Add your acknowledgments here