# Retrieval Augmented Generation (RAG) for LLMs | Prompt Engineering Guide

> **原文链接：** https://www.promptingguide.ai/research/rag
> **处理时间：** 2025-12-31 00:41:29
> **处理方式：** Jina Reader + DeepSeek AI

## 📝 内容摘要

检索增强生成通过外部知识增强大语言模型，以解决领域知识差距和幻觉等问题。  
RAG系统包含索引、检索和生成等核心组件，能够在不重新训练模型的情况下整合最新信息。  
RAG范式已从朴素RAG演进到高级RAG和模块化RAG，以优化检索质量和系统灵活性。  
检索组件可通过分块策略、嵌入模型微调和查询对齐等技术进行增强，提升语义表示准确性。  
RAG在知识密集型应用中尤其有效，能够显著提高响应的准确性、可控性和相关性。

## 🔑 关键概念

- **检索增强生成**: 通过外部知识增强LLM以减少幻觉
- **朴素RAG**: 基础的索引、检索和生成流程
- **高级RAG**: 优化检索前后过程以提升质量
- **模块化RAG**: 可灵活组合功能模块的RAG系统
- **查询重写**: 重写用户查询以优化检索对齐

## 👥 适合人群

这篇文章适合对大型语言模型（LLM）和检索增强生成（RAG）技术有基本了解，并希望深入掌握其原理、范式演变及实际应用的中级技术从业者阅读，例如AI工程师、数据科学家或相关领域的研究人员。

---

## 📄 正文内容

# 面向 LLM 的检索增强生成 | 提示工程指南

在使用 LLM 时存在许多挑战，例如领域知识差距、事实性问题以及幻觉。检索增强生成通过用外部知识（如数据库）增强 LLM，为解决其中一些问题提供了方案。RAG 在知识密集型场景或需要持续更新知识的特定领域应用中特别有用。与其他方法相比，RAG 的一个关键优势是 LLM 无需为特定任务应用进行重新训练。最近，RAG 因其在对话代理中的应用而流行起来。

在本摘要中，我们重点介绍了近期题为《面向大语言模型的检索增强生成：综述》的调查中的主要发现和实践见解。我们特别关注现有的方法、最先进的 RAG、评估、应用以及围绕构成 RAG 系统（检索、生成和增强技术）不同组件的相关技术。

## RAG 简介

![Image 1: "RAG Framework"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-framework.81dc2cdc.png&w=3840&q=75)

正如[此处](https://www.promptingguide.ai/techniques/rag)所介绍的，RAG 可以定义为：

> RAG 接收输入，并根据给定来源（例如，维基百科）检索一组相关/支持性文档。这些文档作为上下文与原始输入提示连接起来，并馈送给文本生成器，由其产生最终输出。这使得 RAG 能够适应事实可能随时间演变的情况。这非常有用，因为 LLM 的参数化知识是静态的。RAG 允许语言模型绕过重新训练，通过基于检索的生成来访问最新信息，从而生成可靠的输出。

简而言之，在 RAG 中获得的检索证据可以作为增强 LLM 响应准确性、可控性和相关性的一种方式。这就是为什么 RAG 有助于减少在高度动态的环境中解决问题时出现的幻觉或性能问题。

虽然 RAG 也涉及预训练方法的优化，但当前的方法已很大程度上转向结合 RAG 和强大微调模型（如 ChatGPT 和 Mixtral）的优势。下图显示了 RAG 相关研究的演变：

![Image 2: "RAG Framework"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-evolution.929ab78b.png&w=1920&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

以下是典型的 RAG 应用工作流程：

![Image 3: "RAG Framework"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-process.c8703891.png&w=1920&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

我们可以将不同的步骤/组件解释如下：

*   **输入：** LLM 系统要回答的问题被称为输入。如果不使用 RAG，则直接使用 LLM 来回答问题。
*   **索引：** 如果使用 RAG，则首先通过分块处理一系列相关文档，生成这些块的嵌入，并将它们索引到向量存储中。在推理时，查询也以类似的方式进行嵌入。
*   **检索：** 通过将查询与索引向量进行比较来获得相关文档，也称为“相关文档”。
*   **生成：** 相关文档与原始提示结合作为附加上下文。然后将组合的文本和提示传递给模型以生成响应，该响应随后被准备为系统给用户的最终输出。

在提供的示例中，由于缺乏对当前事件的了解，直接使用模型无法回答问题。另一方面，当使用 RAG 时，系统可以提取模型适当回答问题所需的相关信息。

## RAG 范式

在过去的几年里，RAG 系统已经从朴素 RAG 发展到高级 RAG 和模块化 RAG。这种演变是为了解决性能、成本和效率方面的某些限制。

![Image 4: "RAG Framework"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-paradigms.21be1d6f.png&w=3840&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

### 朴素 RAG

朴素 RAG 遵循上述传统的索引、检索和生成过程。简而言之，用户输入用于查询相关文档，然后这些文档与提示结合并传递给模型以生成最终响应。如果应用程序涉及多轮对话交互，则可以将对话历史集成到提示中。

朴素 RAG 存在局限性，例如精度低（检索到的块不匹配）和召回率低（未能检索到所有相关块）。LLM 也可能接收到过时的信息，这是 RAG 系统最初应该旨在解决的主要问题之一。这会导致幻觉问题以及糟糕和不准确的响应。

当应用增强时，也可能存在冗余和重复的问题。当使用多个检索到的段落时，排序和协调风格/语气也很关键。另一个挑战是确保生成任务不过度依赖增强信息，否则可能导致模型只是重复检索到的内容。

### 高级 RAG

高级 RAG 有助于处理朴素 RAG 中存在的问题，例如改进检索质量，这可能涉及优化检索前、检索和检索后过程。

检索前过程涉及优化数据索引，旨在通过五个阶段提高被索引数据的质量：增强数据粒度、优化索引结构、添加元数据、对齐优化和混合检索。

检索阶段可以通过优化嵌入模型本身来进一步改进，这直接影响构成上下文的块的质量。这可以通过微调嵌入以优化检索相关性，或采用能更好捕捉上下文理解的动态嵌入（例如，OpenAI 的 embeddings-ada-02 模型）来实现。

优化检索后侧重于避免上下文窗口限制，并处理嘈杂或可能分散注意力的信息。解决这些问题的常见方法是重新排序，这可能涉及将相关上下文重新定位到提示的边缘，或重新计算查询与相关文本块之间的语义相似性。提示压缩也可能有助于处理这些问题。

### 模块化 RAG

顾名思义，模块化 RAG 增强了功能模块，例如集成用于相似性检索的搜索模块，并在检索器中应用微调。朴素 RAG 和高级 RAG 都是模块化 RAG 的特例，由固定模块组成。扩展的 RAG 模块包括搜索、记忆、融合、路由、预测和任务适配器，它们解决了不同的问题。这些模块可以重新排列以适应特定的问题场景。因此，模块化 RAG 的优势在于其更高的多样性和灵活性，您可以根据任务需求添加或替换模块，或调整模块间的流程。

鉴于构建 RAG 系统的灵活性增加，人们提出了其他重要的优化技术来优化 RAG 流程，包括：

*   **混合搜索探索：** 这种方法结合了基于关键字的搜索和语义搜索等多种搜索技术，以检索相关且上下文丰富的信息；这在处理不同类型的查询和信息需求时非常有用。
*   **递归检索与查询引擎：** 涉及一个递归检索过程，可能从小的语义块开始，随后检索更大的块以丰富上下文；这对于平衡效率和上下文丰富的信息很有用。
*   **StepBack-prompt：** [一种提示技术（在新标签页中打开）](https://arxiv.org/abs/2310.06117)，使 LLM 能够进行抽象，产生指导推理的概念和原则；当应用于 RAG 框架时，这能带来更可靠的响应，因为 LLM 脱离了具体实例，并在需要时可以进行更广泛的推理。
*   **子查询：** 存在不同的查询策略，例如树状查询或对块的顺序查询，可用于不同的场景。LlamaIndex 提供了一个 [子问题查询引擎（在新标签页中打开）](https://docs.llamaindex.ai/en/latest/understanding/putting_it_all_together/agents.html#)，允许将一个查询分解为几个使用不同相关数据源的问题。
*   **假设文档嵌入：** [HyDE（在新标签页中打开）](https://arxiv.org/abs/2212.10496) 为查询生成一个假设答案，将其嵌入，并使用它来检索与假设答案相似的文档，而不是直接使用查询。

RAG 框架[](https://www.promptingguide.ai/research/rag#rag-framework)
-------------------------------------------------------------------------

在本节中，我们总结了 RAG 系统各组成部分的关键发展，包括检索、生成和增强。

### 检索[](https://www.promptingguide.ai/research/rag#retrieval)

检索是 RAG 中负责从检索器中检索高度相关上下文的组件。检索器可以通过多种方式增强，包括：

**增强语义表示**

此过程涉及直接改进驱动检索器的语义表示。以下是一些考虑因素：

*   **分块：** 一个重要步骤是选择合适的分块策略，这取决于您处理的内容以及您为之生成响应的应用程序。不同的模型在不同块大小上也表现出不同的优势。Sentence transformers 在单句上表现更好，但 text-embedding-ada-002 在包含 256 或 512 个 token 的块上表现更好。其他需要考虑的方面包括用户问题的长度、应用程序和 token 限制，但通常需要尝试不同的分块策略来帮助优化 RAG 系统中的检索。
*   **微调嵌入模型：** 一旦确定了有效的分块策略，如果您在专业领域工作，可能需要微调嵌入模型。否则，用户查询在您的应用程序中可能会被完全误解。您可以在广泛的领域知识（即领域知识微调）和特定的下游任务上进行微调。[BGE-large-EN 由 BAAI 开发（在新标签页中打开）](https://github.com/FlagOpen/FlagEmbedding) 是一个值得注意的嵌入模型，可以通过微调来优化检索相关性。

**对齐查询和文档**

此过程处理将用户的查询与语义空间中的文档对齐。当用户的查询可能缺乏语义信息或包含不精确的措辞时，可能需要这样做。以下是一些方法：

*   **查询重写：** 侧重于使用各种技术重写查询，例如 [Query2Doc（在新标签页中打开）](https://arxiv.org/abs/2303.07678)、[ITER-RETGEN（在新标签页中打开）](https://arxiv.org/abs/2305.15294) 和 HyDE。
*   **嵌入转换：** 优化查询嵌入的表示，并将其对齐到与任务更紧密相关的潜在空间。

**对齐检索器和 LLM**

此过程处理将检索器输出与 LLM 的偏好对齐。

*   **微调检索器：** 使用 LLM 的反馈信号来优化检索模型。示例包括增强适应检索器（[AAR（在新标签页中打开）](https://arxiv.org/abs/2305.17331)）、[REPLUG（在新标签页中打开）](https://arxiv.org/abs/2301.12652) 和 [UPRISE（在新标签页中打开）](https://arxiv.org/abs/2303.08518) 等。
*   **适配器：** 集成外部适配器以帮助对齐过程。示例包括 [PRCA（在新标签页中打开）](https://aclanthology.org/2023.emnlp-main.326/)、[RECOMP（在新标签页中打开）](https://arxiv.org/abs/2310.04408) 和 [PKG（在新标签页中打开）](https://arxiv.org/abs/2305.04757)。

### 生成[](https://www.promptingguide.ai/research/rag#generation)

RAG 系统中的生成器负责将检索到的信息转换为连贯的文本，形成模型的最终输出。此过程涉及多样化的输入数据，有时需要努力改进语言模型对来自查询和文档的输入数据的适应。这可以通过后检索处理和微调来解决：

*   **使用冻结 LLM 进行后检索：** 后检索处理保持 LLM 不变，而是专注于通过信息压缩和结果重排等操作来提高检索结果的质量。信息压缩有助于减少噪声、解决 LLM 的上下文长度限制并增强生成效果。重排旨在重新排序文档，将最相关的项目优先放在顶部。
*   **为 RAG 微调 LLM：** 为了改进 RAG 系统，可以进一步优化或微调生成器，以确保生成的文本自然并有效利用检索到的文档。

### 增强[](https://www.promptingguide.ai/research/rag#augmentation)

增强涉及将检索到的段落中的上下文与当前生成任务有效整合的过程。在进一步讨论增强过程、增强阶段和增强数据之前，以下是 RAG 核心组件的分类：

![图 5："RAG 分类"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-taxonomy.e3b19705.png&w=3840&q=75)_[图片来源（在新标签页中打开）](https://arxiv.org/abs/2312.10997)_

检索增强可以应用于许多不同的阶段，例如预训练、微调和推理。

*   **增强阶段：** [RETRO（在新标签页中打开）](https://arxiv.org/abs/2112.04426) 是一个利用检索增强进行大规模从头预训练的系统示例；它使用建立在外部知识之上的额外编码器。微调也可以与 RAG 结合，以帮助开发和改进 RAG 系统的有效性。在推理阶段，应用了许多技术来有效整合检索到的内容，以满足特定任务需求并进一步优化 RAG 过程。

*   **增强源**：RAG 模型的有效性在很大程度上受增强数据源选择的影响。数据可分为非结构化数据、结构化数据和 LLM 生成的数据。

*   **增强过程**：对于许多问题（例如多步推理），单次检索是不够的，因此已经提出了一些方法：

    *   **迭代检索** 使模型能够执行多个检索周期，以增强信息的深度和相关性。利用此方法的著名方法包括 [RETRO](https://arxiv.org/abs/2112.04426) 和 [GAR-meets-RAG](https://arxiv.org/abs/2310.20158)。
    *   **递归检索** 将一个检索步骤的输出作为另一个检索步骤的输入进行递归迭代；这使得能够为复杂和多步骤的查询（例如，学术研究和法律案例分析）更深入地挖掘相关信息。利用此方法的著名方法包括 [IRCoT](https://arxiv.org/abs/2212.10509) 和 [Tree of Clarifications](https://arxiv.org/abs/2310.14696)。
    *   **自适应检索** 通过确定检索的最佳时机和内容，使检索过程适应特定需求。利用此方法的著名方法包括 [FLARE](https://arxiv.org/abs/2305.06983) 和 [Self-RAG](https://arxiv.org/abs/2310.11511)。

下图详细描述了 RAG 研究的不同增强方面，包括增强阶段、源和过程。

![Image 6: "RAG Augmentation Aspects"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-augmentation.0855501d.png&w=3840&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

### RAG vs. 微调

关于 RAG 和微调之间的区别以及各自适用的场景有很多公开讨论。这两个领域的研究表明，RAG 适用于整合新知识，而微调则可用于通过改进内部知识、输出格式和教授复杂的指令遵循来提高模型性能和效率。这些方法并不相互排斥，可以在一个迭代过程中相互补充，旨在改进 LLM 的使用，以应对需要访问快速发展的知识并生成遵循特定格式、语气和风格的定制化响应的复杂知识密集型且可扩展的应用程序。此外，提示工程也可以通过利用模型的固有能力来帮助优化结果。下图显示了 RAG 与其他模型优化方法相比的不同特征：

![Image 7: "RAG Optimization"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-optimization.bb88c6ae.png&w=3840&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

以下是调查论文中比较 RAG 和微调模型特性的表格：

![Image 8: "RAG Augmentation Aspects"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-vs-finetuning.545747e9.png&w=1920&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

### RAG 评估

与衡量 LLM 在不同方面的性能类似，评估在理解和优化 RAG 模型在不同应用场景中的性能方面起着关键作用。传统上，RAG 系统是基于下游任务的表现来评估的，使用特定于任务的指标，如 F1 和 EM。[RaLLe](https://arxiv.org/abs/2308.10633v2) 是一个著名的框架示例，用于评估用于知识密集型任务的检索增强大语言模型。

RAG 评估目标针对检索和生成两方面确定，其目标是评估检索到的上下文质量和生成的内容质量。为了评估检索质量，使用了其他知识密集型领域（如推荐系统和信息检索）中使用的指标，如 NDCG 和命中率。为了评估生成质量，可以评估不同方面，如相关性、有害性（如果是未标记内容）或准确性（对于已标记内容）。总体而言，RAG 评估可以涉及手动或自动评估方法。

评估 RAG 框架主要关注三个质量分数和四种能力。质量分数包括测量上下文相关性（即检索到的上下文的精确性和特异性）、答案忠实度（即答案对检索到的上下文的忠实程度）和答案相关性（即答案与所提问题的相关性）。此外，还有四种能力有助于衡量 RAG 系统的适应性和效率：噪声鲁棒性、负面拒绝、信息整合和反事实鲁棒性。以下是用于评估 RAG 系统不同方面的指标总结：

![Image 9: "RAG Augmentation Aspects"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-metrics.1ddc2a61.png&w=1920&q=75)_[Figure Source](https://arxiv.org/abs/2312.10997)_

有几个基准，如 [RGB](https://arxiv.org/abs/2309.01431) 和 [RECALL](https://arxiv.org/abs/2311.08147)，用于评估 RAG 模型。许多工具，如 [RAGAS](https://arxiv.org/abs/2309.15217)、[ARES](https://arxiv.org/abs/2311.09476) 和 [TruLens](https://www.trulens.org/trulens_eval/core_concepts_rag_triad/)，已被开发来自动化评估 RAG 系统的过程。其中一些系统依赖 LLM 来确定上述定义的一些质量分数。

### RAG 的挑战与未来

在本概述中，我们讨论了 RAG 研究的几个方面，以及增强 RAG 系统检索、增强和生成的不同方法。以下是 [Gao et al., 2023](https://arxiv.org/abs/2312.10997) 强调的在我们继续开发和改进 RAG 系统时面临的几个挑战：

*   **上下文长度：** LLM 持续扩展上下文窗口大小，这对 RAG 如何适应以确保捕获高度相关和重要的上下文提出了挑战。
*   **鲁棒性：** 处理反事实和对抗性信息对于衡量和改进 RAG 非常重要。
*   **混合方法：** 正在进行研究，以更好地理解如何优化 RAG 和微调模型的使用。
*   **扩展 LLM 角色：** 增加 LLM 的角色和能力以进一步增强 RAG 系统备受关注。
*   **缩放定律：** 对 LLM 缩放定律及其如何应用于 RAG 系统的研究仍未得到充分理解。
*   **生产就绪的 RAG：** 生产级 RAG 系统要求在性能、效率、数据安全、隐私等方面具备卓越的工程能力。
*   **多模态 RAG：** 尽管围绕 RAG 系统已有大量研究工作，但它们主要集中在基于文本的任务上。人们越来越有兴趣扩展 RAG 系统的模态，以支持解决更多领域的问题，如图像、音频和视频、代码等。
*   **评估：** 使用 RAG 构建复杂应用程序的兴趣，需要特别关注开发细致的指标和评估工具，以更可靠地评估上下文相关性、创造性、内容多样性、事实性等不同方面。此外，还需要针对 RAG 进行更好的可解释性研究和工具开发。

RAG 工具[](https://www.promptingguide.ai/research/rag#rag-tools)
-----------------------------------------------------------------

一些用于构建 RAG 系统的流行综合工具包括 [LangChain (opens in a new tab)](https://www.langchain.com/)、[LlamaIndex (opens in a new tab)](https://www.llamaindex.ai/) 和 [DSPy (opens in a new tab)](https://github.com/stanfordnlp/dspy)。还有一系列服务于不同目的的专业工具，例如 [Flowise AI (opens in a new tab)](https://flowiseai.com/)，它提供了构建 RAG 应用程序的低代码解决方案。其他值得注意的技术包括 [HayStack (opens in a new tab)](https://haystack.deepset.ai/)、[Meltano (opens in a new tab)](https://meltano.com/)、[Cohere Coral (opens in a new tab)](https://cohere.com/coral) 等。软件和云服务提供商也正在纳入以 RAG 为中心的服务。例如，来自 Weaviate 的 Verba 可用于构建个人助理应用程序，而亚马逊的 Kendra 则提供智能企业搜索服务。

结论[](https://www.promptingguide.ai/research/rag#conclusion)
-------------------------------------------------------------------

总之，RAG 系统发展迅速，包括开发更先进的范式，这些范式支持定制化，并进一步提升了 RAG 在广泛领域的性能和实用性。市场对 RAG 应用程序的需求巨大，这加速了改进 RAG 系统各个组件的方法的开发。从混合方法到自检索，这些都是当前现代 RAG 模型正在探索的研究领域。市场对更好的评估工具和指标的需求也在不断增长。下图总结了本文概述中涉及的 RAG 生态系统、增强 RAG 的技术、挑战及其他相关方面：

![Image 10: "RAG Ecosystem"](https://www.promptingguide.ai/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Frag-ecosystem.b7b7d408.png&w=1920&q=75)_[Figure Source (opens in a new tab)](https://arxiv.org/abs/2312.10997)_

* * *

RAG 研究洞见[](https://www.promptingguide.ai/research/rag#rag-research-insights)
-----------------------------------------------------------------------------------------

以下是一系列研究论文，重点介绍了 RAG 的关键见解和最新进展。

参考文献[](https://www.promptingguide.ai/research/rag#references)
-------------------------------------------------------------------

*   [KAUCUS: Knowledge Augmented User Simulators for Training Language Model Assistants (opens in a new tab)](https://aclanthology.org/2024.scichat-1.5)
*   [A Survey on Hallucination in Large Language Models: Principles,Taxonomy, Challenges, and Open Questions (opens in a new tab)](https://arxiv.org/abs/2311.05232)
*   [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (opens in a new tab)](https://arxiv.org/abs/2005.11401)
*   [Retrieval-augmented multimodal language modeling (opens in a new tab)](https://arxiv.org/abs/2211.12561)
*   [In-Context Retrieval-Augmented Language Models (opens in a new tab)](https://arxiv.org/abs/2302.00083)
*   [Precise Zero-Shot Dense Retrieval without Relevance Labels (opens in a new tab)](https://arxiv.org/abs/2212.10496)
*   [Shall we pretrain autoregressive language models with retrieval? a comprehensive study. (opens in a new tab)](https://arxiv.org/pdf/2312.10997.pdf)
*   [REPLUG: Retrieval-Augmented Black-Box Language Models (opens in a new tab)](https://arxiv.org/abs/2301.12652)
*   [Query2Doc (opens in a new tab)](https://arxiv.org/abs/2303.07678)
*   [ITER-RETGEN (opens in a new tab)](https://arxiv.org/abs/2305.15294)
*   [A Survey of Techniques for Maximizing LLM Performance (opens in a new tab)](https://youtu.be/ahnGLM-RC1Y?si=z45qrLTPBfMe15LM)
*   [HyDE (opens in a new tab)](https://arxiv.org/abs/2212.10496)
*   [Advanced RAG Techniques: an Illustrated Overview (opens in a new tab)](https://pub.towardsai.net/advanced-rag-techniques-an-illustrated-overview-04d193d8fec6)
*   [Best Practices for LLM Evaluation of RAG Applications (opens in a new tab)](https://www.databricks.com/blog/LLM-auto-eval-best-practices-RAG)
*   [Building Production-Ready RAG Applications (opens in a new tab)](https://youtu.be/TRjq7t2Ms5I?si=gywRj82NIc-wsHcF)
*   [Evaluating RAG Part I: How to Evaluate Document Retrieval (opens in a new tab)](https://www.deepset.ai/blog/rag-evaluation-retrieval)
*   [Retrieval Augmented Generation meets Reciprocal Rank Fusion and Generated Queries (opens in a new tab)](https://towardsdatascience.com/forget-rag-the-future-is-rag-fusion-1147298d8ad1)

最后更新于 2025年12月20日 星期六

赞助商 [![Image 11: SerpAPI](https://cdn.rawgit.com/standard/standard/master/docs/logos/serpapi.png)](https://serpapi.com/)

[LLM Agents](https://www.promptingguide.ai/research/llm-agents "LLM Agents")[LLM Reasoning](https://www.promptingguide.ai/research/llm-reasoning "LLM Reasoning")
