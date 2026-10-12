window.__AWESOME_FREE_PROVIDERS__ = [
  {
    "provider": "NVIDIA NIM",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "key_url": "https://build.nvidia.com/settings/api-keys",
    "credit_card": "Phone verification",
    "free_models_count": "132",
    "max_context": "1M",
    "modalities": "audio, embedding, image, pdf, reasoning, rerank, text, video, vision",
    "best_models": [
      {
        "name": "z-ai/glm-5.3-flash",
        "id": "z-ai/glm-5.3-flash",
        "context": "1M",
        "rate_limit": "Up to 40 RPM"
      },
      {
        "name": "z-ai/glm-5.2",
        "id": "z-ai/glm-5.2",
        "context": "1M",
        "rate_limit": "Up to 40 RPM"
      },
      {
        "name": "z-ai/glm-5.1",
        "id": "z-ai/glm-5.1",
        "context": "202K",
        "rate_limit": "Up to 40 RPM"
      }
    ]
  },
  {
    "provider": "ModelScope",
    "base_url": "https://api-inference.modelscope.cn/v1",
    "key_url": "https://modelscope.cn/my/myaccesstoken",
    "credit_card": "Registration",
    "free_models_count": "61",
    "max_context": "1M",
    "modalities": "audio, image, reasoning, text, video, vision",
    "best_models": [
      {
        "name": "MiniMax-M2.5-highspeed",
        "id": "MiniMax/MiniMax-M2.5",
        "context": "204K",
        "rate_limit": "See provider"
      },
      {
        "name": "Qwen/Qwen3.5-35B-A3B",
        "id": "qwen-qwen3-5-35b-a3b",
        "context": "256K",
        "rate_limit": "2,000 RPD total; &lt;=500 .."
      },
      {
        "name": "Qwen/Qwen3.5-27B",
        "id": "qwen-qwen3-5-27b",
        "context": "256K",
        "rate_limit": "2,000 RPD total; &lt;=500 .."
      }
    ]
  },
  {
    "provider": "Cloudflare Workers AI",
    "base_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run",
    "key_url": "https://dash.cloudflare.com/profile/api-tokens",
    "credit_card": "No",
    "free_models_count": "40",
    "max_context": "262K",
    "modalities": "code, image, reasoning, text, video",
    "best_models": [
      {
        "name": "Mistral 7B",
        "id": "@cf/mistral/mistral-7b-instruct-v0.1",
        "context": "32K",
        "rate_limit": "See provider"
      },
      {
        "name": "Qwen 1.5 7B",
        "id": "@cf/qwen/qwen1.5-7b-chat",
        "context": "32K",
        "rate_limit": "See provider"
      },
      {
        "name": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "id": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "context": "24K",
        "rate_limit": "10K neurons/day (shared)"
      }
    ]
  },
  {
    "provider": "OpenCode Zen",
    "base_url": "https://opencode.ai/zen/v1",
    "key_url": "https://opencode.ai/auth",
    "credit_card": "Registration",
    "free_models_count": "34",
    "max_context": "1M",
    "modalities": "audio, reasoning, vision",
    "best_models": [
      {
        "name": "big-pickle",
        "id": "big-pickle",
        "context": "0",
        "rate_limit": ""
      },
      {
        "name": "DeepSeek V4 Flash",
        "id": "deepseek-v4-flash-free",
        "context": "1M",
        "rate_limit": ""
      },
      {
        "name": "MiMo-V2.5",
        "id": "mimo-v2.5-free",
        "context": "1M",
        "rate_limit": ""
      }
    ]
  },
  {
    "provider": "OpenRouter",
    "base_url": "https://openrouter.ai/api/v1",
    "key_url": "https://openrouter.ai/workspaces/default/keys",
    "credit_card": "Registration",
    "free_models_count": "3",
    "max_context": "128K",
    "modalities": "text",
    "best_models": [
      {
        "name": "NVIDIA: Nemotron 3 Ultra (free)",
        "id": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "context": "1M",
        "rate_limit": "See provider"
      },
      {
        "name": "Poolside: Laguna S 2.1 (free)",
        "id": "poolside/laguna-s-2.1:free",
        "context": "262K",
        "rate_limit": "See provider"
      },
      {
        "name": "Poolside: Laguna M.1 (free)",
        "id": "poolside/laguna-m.1:free",
        "context": "262K",
        "rate_limit": "See provider"
      }
    ]
  },
  {
    "provider": "LLM7.io",
    "base_url": "https://api.llm7.io/v1",
    "key_url": "https://token.llm7.io",
    "credit_card": "No",
    "free_models_count": "24",
    "max_context": "1M",
    "modalities": "audio, code, image, pdf, reasoning, text, video, vision",
    "best_models": [
      {
        "name": "gpt-oss:20b",
        "id": "gpt-oss-20b",
        "context": "128K",
        "rate_limit": "60 RPM, 250 req/hr (fre.."
      },
      {
        "name": "mistral-Nemo-Instruct-2407",
        "id": "mistral-Nemo-Instruct-2407",
        "context": "128K",
        "rate_limit": "60 RPM, 250 req/hr (fre.."
      },
      {
        "name": "minimax-m2.7",
        "id": "minimax-m2.7",
        "context": "180K",
        "rate_limit": "60 RPM, 250 req/hr (fre.."
      }
    ]
  },
  {
    "provider": "Kilo Code",
    "base_url": "https://api.kilo.ai/api/gateway",
    "key_url": "https://app.kilo.ai/profile",
    "credit_card": "No",
    "free_models_count": "22",
    "max_context": "1M",
    "modalities": "audio, code, image, reasoning, text, video",
    "best_models": [
      {
        "name": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "id": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "context": "1M",
        "rate_limit": "200 req/hr"
      },
      {
        "name": "stepfun/step-3.7-flash:free",
        "id": "stepfun/step-3.7-flash:free",
        "context": "262K",
        "rate_limit": "200 req/hr"
      },
      {
        "name": "nvidia/nemotron-3-super-120b-a12b:free",
        "id": "nvidia/nemotron-3-super-120b-a12b:free",
        "context": "262K",
        "rate_limit": "200 req/hr"
      }
    ]
  },
  {
    "provider": "Google Gemini",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "key_url": "https://aistudio.google.com/app/apikey",
    "credit_card": "No",
    "free_models_count": "19",
    "max_context": "1M",
    "modalities": "audio, image, pdf, reasoning, text, video, vision",
    "best_models": [
      {
        "name": "Gemini 3.8 Flash",
        "id": "gemini-3.8-flash",
        "context": "1M",
        "rate_limit": "—"
      },
      {
        "name": "Gemini 3.7 Flash",
        "id": "gemini-3.7-flash",
        "context": "1M",
        "rate_limit": "—"
      },
      {
        "name": "Gemini 3.6 Flash",
        "id": "gemini-3.6-flash",
        "context": "1M",
        "rate_limit": "15 RPM, 1,500 RPD"
      }
    ]
  },
  {
    "provider": "Ollama Cloud",
    "base_url": "https://ollama.com/api",
    "key_url": "https://ollama.com/settings/keys",
    "credit_card": "Registration",
    "free_models_count": "17",
    "max_context": "1M",
    "modalities": "code, image, reasoning, text, video, vision",
    "best_models": [
      {
        "name": "deepseek-v4-pro",
        "id": "deepseek-v4-pro",
        "context": "1M",
        "rate_limit": "Session/weekly limits (.."
      },
      {
        "name": "deepseek-v4-flash",
        "id": "deepseek-v4-flash",
        "context": "1M",
        "rate_limit": "Session/weekly limits (.."
      },
      {
        "name": "minimax-m3",
        "id": "minimax-m3",
        "context": "512K",
        "rate_limit": "Session/weekly limits (.."
      }
    ]
  },
  {
    "provider": "Mistral AI",
    "base_url": "https://api.mistral.ai/v1",
    "key_url": "https://console.mistral.ai/api-keys",
    "credit_card": "No",
    "free_models_count": "15",
    "max_context": "256K",
    "modalities": "code, image, text",
    "best_models": [
      {
        "name": "Mistral 7B",
        "id": "open-mistral-7b",
        "context": "32K",
        "rate_limit": "See provider"
      },
      {
        "name": "Mixtral 8x7B",
        "id": "open-mixtral-8x7b",
        "context": "32K",
        "rate_limit": "See provider"
      },
      {
        "name": "Mistral Medium 3.5 (128B)",
        "id": "mistral-medium-3-5-128b",
        "context": "256K",
        "rate_limit": "~1 RPS, 500K TPM"
      }
    ]
  },
  {
    "provider": "OVHcloud AI Endpoints",
    "base_url": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
    "key_url": "https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/",
    "credit_card": "Registration",
    "free_models_count": "15",
    "max_context": "262K",
    "modalities": "audio, code, image, reasoning, text, video",
    "best_models": [
      {
        "name": "Qwen3.5-397B-A17B",
        "id": "qwen3.5-397b-a17b",
        "context": "262K",
        "rate_limit": "2 RPM (anonymous)"
      },
      {
        "name": "Meta-Llama-3_3-70B-Instruct",
        "id": "meta-llama-3_3-70b-instruct",
        "context": "131K",
        "rate_limit": "2 RPM (anonymous)"
      },
      {
        "name": "Qwen3.8-27B",
        "id": "qwen3.8-27b",
        "context": "262K",
        "rate_limit": "2 RPM (anonymous)"
      }
    ]
  },
  {
    "provider": "Groq",
    "base_url": "https://api.groq.com/openai/v1",
    "key_url": "https://console.groq.com/keys",
    "credit_card": "No",
    "free_models_count": "12",
    "max_context": "262K",
    "modalities": "image, reasoning, text",
    "best_models": [
      {
        "name": "Moonshot Kimi K2",
        "id": "moonshotai/kimi-k2-instruct",
        "context": "131K",
        "rate_limit": "See provider"
      },
      {
        "name": "Moonshot Kimi K2 0905",
        "id": "moonshotai/kimi-k2-instruct-0905",
        "context": "131K",
        "rate_limit": "See provider"
      },
      {
        "name": "groq/compound",
        "id": "groq/compound",
        "context": "131K",
        "rate_limit": "30 RPM, 250 RPD"
      }
    ]
  },
  {
    "provider": "Cohere",
    "base_url": "https://api.cohere.com/v2",
    "key_url": "https://dashboard.cohere.com/api-keys",
    "credit_card": "No",
    "free_models_count": "12",
    "max_context": "256K",
    "modalities": "image, text",
    "best_models": [
      {
        "name": "Command A+ (218B)",
        "id": "command-a-218b",
        "context": "128K",
        "rate_limit": "20 RPM"
      },
      {
        "name": "Command A (111B)",
        "id": "command-a-111b",
        "context": "256K",
        "rate_limit": "20 RPM"
      },
      {
        "name": "Command R+",
        "id": "command-r",
        "context": "128K",
        "rate_limit": "20 RPM"
      }
    ]
  },
  {
    "provider": "Aion Labs",
    "base_url": "https://api.aionlabs.ai/v1",
    "key_url": "https://www.aionlabs.ai/app/api-keys/",
    "credit_card": "Registration",
    "free_models_count": "11",
    "max_context": "131K",
    "modalities": "text",
    "best_models": [
      {
        "name": "aion-labs/aion-2.0",
        "id": "aion-labs-aion-2-0",
        "context": "128K",
        "rate_limit": "15 RPM, 20K TPD"
      },
      {
        "name": "aion-labs/aion-rp-llama-3.1-8b",
        "id": "aion-labs-aion-rp-llama-3-1-8b",
        "context": "32K",
        "rate_limit": "15 RPM, 20K TPD"
      },
      {
        "name": "aion-labs/aion-3.0",
        "id": "aion-labs-aion-3-0",
        "context": "128K",
        "rate_limit": "15 RPM, 20K TPD"
      }
    ]
  },
  {
    "provider": "Hugging Face",
    "base_url": "https://router.huggingface.co/v1",
    "key_url": "https://huggingface.co/settings/tokens",
    "credit_card": "No",
    "free_models_count": "9",
    "max_context": "131K",
    "modalities": "code, image, text",
    "best_models": [
      {
        "name": "Meta-Llama-3.1-8B-Instruct",
        "id": "meta-llama-3-1-8b-instruct",
        "context": "128K",
        "rate_limit": "Credit-metered"
      },
      {
        "name": "gemma-3-4b-it",
        "id": "google/gemma-3-4b-it",
        "context": "131K",
        "rate_limit": "Credit-metered"
      },
      {
        "name": "phi-4",
        "id": "phi-4",
        "context": "16K",
        "rate_limit": "Credit-metered"
      }
    ]
  },
  {
    "provider": "Z AI (Zhipu AI)",
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "key_url": "https://open.bigmodel.cn/usercenter/apikeys",
    "credit_card": "No",
    "free_models_count": "8",
    "max_context": "200K",
    "modalities": "image, reasoning, text, video",
    "best_models": [
      {
        "name": "GLM-4.7-Flash",
        "id": "glm-4.7-flash",
        "context": "200K",
        "rate_limit": "1 concurrent request"
      },
      {
        "name": "GLM-4.5-Flash (retirement announced)",
        "id": "glm-4-5-flash-retirement-announced",
        "context": "128K",
        "rate_limit": "1 concurrent request"
      },
      {
        "name": "GLM-4.6V-Flash",
        "id": "glm-4.6v-flash",
        "context": "128K",
        "rate_limit": "1 concurrent request"
      }
    ]
  },
  {
    "provider": "Cerebras",
    "base_url": "https://api.cerebras.ai/v1",
    "key_url": "https://cloud.cerebras.ai/",
    "credit_card": "No",
    "free_models_count": "6",
    "max_context": "131K",
    "modalities": "reasoning, text",
    "best_models": [
      {
        "name": "Llama 3.1 70B",
        "id": "llama3.1-70b",
        "context": "131K",
        "rate_limit": "See provider"
      },
      {
        "name": "zai-glm-4.7 (deprecated Aug 2026)",
        "id": "zai-glm-4-7-deprecated-aug-2026",
        "context": "131K",
        "rate_limit": "5 RPM, 30K TPM, 1M TPD"
      },
      {
        "name": "zai-glm-4.7",
        "id": "zai-glm-4.7",
        "context": "128K",
        "rate_limit": "10 RPM, 100 RPD, 1M TPD"
      }
    ]
  },
  {
    "provider": "Agnes AI",
    "base_url": "https://apihub.agnes-ai.com/v1",
    "key_url": "https://platform.agnes-ai.com/settings/apiKeys",
    "credit_card": "Registration",
    "free_models_count": "5",
    "max_context": "256K",
    "modalities": "image, reasoning, text, video, vision",
    "best_models": [
      {
        "name": "agnes-1.5-flash",
        "id": "agnes-1.5-flash",
        "context": "256K",
        "rate_limit": "30 RPM"
      },
      {
        "name": "agnes-2.0-flash",
        "id": "agnes-2.0-flash",
        "context": "256K",
        "rate_limit": "30 RPM"
      },
      {
        "name": "agnes-image-2.0-flash",
        "id": "agnes-image-2.0-flash",
        "context": "4K",
        "rate_limit": "30 RPM (1K)"
      }
    ]
  },
  {
    "provider": "Alibaba Cloud Model Studio",
    "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "key_url": "https://bailian.console.alibabacloud.com/?apiKey=1",
    "credit_card": "Registration",
    "free_models_count": "5",
    "max_context": "1M",
    "modalities": "code, image, text",
    "best_models": [
      {
        "name": "Qwen3-Max",
        "id": "qwen3-max",
        "context": "128K",
        "rate_limit": "Tiered by region"
      },
      {
        "name": "Qwen3-Plus",
        "id": "qwen3-plus",
        "context": "1M",
        "rate_limit": "Tiered by region"
      },
      {
        "name": "Qwen3-VL-Plus",
        "id": "qwen3-vl-plus",
        "context": "128K",
        "rate_limit": "Tiered by region"
      }
    ]
  },
  {
    "provider": "SambaNova",
    "base_url": "https://api.sambanova.ai/v1",
    "key_url": "https://cloud.sambanova.ai/apis",
    "credit_card": "Registration",
    "free_models_count": "4",
    "max_context": "128K",
    "modalities": "image, reasoning, text",
    "best_models": [
      {
        "name": "DeepSeek-V3.1",
        "id": "deepseek-v3-1",
        "context": "128K",
        "rate_limit": "20 RPM, 20 RPD, 200K TPD"
      },
      {
        "name": "DeepSeek-V3.2 (Preview)",
        "id": "deepseek-v3-2-preview",
        "context": "128K",
        "rate_limit": "20 RPM, 20 RPD, 200K TPD"
      },
      {
        "name": "MiniMax-M2.7",
        "id": "minimax-m2-7",
        "context": "128K",
        "rate_limit": "20 RPM, 20 RPD, 200K TPD"
      }
    ]
  },
  {
    "provider": "SiliconFlow",
    "base_url": "https://api.siliconflow.cn/v1",
    "key_url": "https://cloud.siliconflow.cn/account/ak",
    "credit_card": "Registration",
    "free_models_count": "3",
    "max_context": "131K",
    "modalities": "text",
    "best_models": [
      {
        "name": "Abbreviation",
        "id": "abbreviation",
        "context": "131K",
        "rate_limit": "See provider"
      },
      {
        "name": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "id": "deepseek-ai-deepseek-r1-distill-qwen-7b",
        "context": "131K",
        "rate_limit": "30 RPM, 60K TPM"
      },
      {
        "name": "deepseek-ai/DeepSeek-OCR",
        "id": "deepseek-ai-deepseek-ocr",
        "context": "131K",
        "rate_limit": "30 RPM, 60K TPM"
      }
    ]
  },
  {
    "provider": "xAI",
    "base_url": "https://api.x.ai/v1",
    "key_url": "https://console.x.ai",
    "credit_card": "Registration",
    "free_models_count": "3",
    "max_context": "2M",
    "modalities": "text",
    "best_models": [
      {
        "name": "grok-4.3",
        "id": "grok-4-3",
        "context": "1M",
        "rate_limit": "Credit-based"
      },
      {
        "name": "grok-4.1-fast",
        "id": "grok-4-1-fast",
        "context": "2M",
        "rate_limit": "Credit-based"
      },
      {
        "name": "grok-3-mini",
        "id": "grok-3-mini",
        "context": "131K",
        "rate_limit": "Credit-based"
      }
    ]
  },
  {
    "provider": "Cline",
    "base_url": "``",
    "key_url": "/open-free-llm-api/awesome-freellm-apis/blob/main",
    "credit_card": "Registration",
    "free_models_count": "3",
    "max_context": "0",
    "modalities": "text",
    "best_models": [
      {
        "name": "Muse Spark 1.3 Contributor",
        "id": "cline-free/muse-spark-1.3-contributor",
        "context": "0",
        "rate_limit": "See provider"
      },
      {
        "name": "Mimo V2.6 Flash",
        "id": "cline-free/mimo-v2.6-flash",
        "context": "0",
        "rate_limit": "See provider"
      },
      {
        "name": "Solar Mini 4",
        "id": "cline-free/solar-mini4",
        "context": "0",
        "rate_limit": "See provider"
      }
    ]
  },
  {
    "provider": "Chutes.ai",
    "base_url": "https://api.chutes.ai/v1",
    "key_url": "https://chutes.ai/",
    "credit_card": "Registration",
    "free_models_count": "2",
    "max_context": "131K",
    "modalities": "reasoning, text",
    "best_models": [
      {
        "name": "DeepSeek-R1",
        "id": "deepseek-ai/DeepSeek-R1",
        "context": "131K",
        "rate_limit": "Community-powered, no h.."
      },
      {
        "name": "Llama 3.1 70B",
        "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "context": "131K",
        "rate_limit": "Community-powered, no h.."
      }
    ]
  },
  {
    "provider": "Glhf.chat",
    "base_url": "https://glhf.chat/api/openai/v1",
    "key_url": "https://glhf.chat/",
    "credit_card": "Registration",
    "free_models_count": "2",
    "max_context": "131K",
    "modalities": "text",
    "best_models": [
      {
        "name": "Llama 3.1 70B",
        "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "context": "131K",
        "rate_limit": "Unlimited for free models"
      },
      {
        "name": "Mixtral 8x7B",
        "id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "context": "32K",
        "rate_limit": "Unlimited for free models"
      }
    ]
  },
  {
    "provider": "Grok (xAI)",
    "base_url": "https://api.x.ai/v1",
    "key_url": "https://console.x.ai/",
    "credit_card": "Registration",
    "free_models_count": "2",
    "max_context": "131K",
    "modalities": "text",
    "best_models": [
      {
        "name": "Grok-2",
        "id": "grok-2",
        "context": "131K",
        "rate_limit": "$25/month free credits,.."
      },
      {
        "name": "Grok-2 Mini",
        "id": "grok-2-mini",
        "context": "131K",
        "rate_limit": "$25/month free credits,.."
      }
    ]
  },
  {
    "provider": "AI21 Labs",
    "base_url": "https://api.ai21.com/studio/v1",
    "key_url": "https://studio.ai21.com/account/api-key",
    "credit_card": "Registration",
    "free_models_count": "2",
    "max_context": "256K",
    "modalities": "text",
    "best_models": [
      {
        "name": "Jamba Large 1.7",
        "id": "jamba-large-1-7",
        "context": "256K",
        "rate_limit": "200 RPM, 10 RPS"
      },
      {
        "name": "Jamba Mini 2",
        "id": "jamba-mini-2",
        "context": "256K",
        "rate_limit": "200 RPM, 10 RPS"
      }
    ]
  },
  {
    "provider": "DeepSeek",
    "base_url": "https://api.deepseek.com/v1",
    "key_url": "https://platform.deepseek.com/api_keys",
    "credit_card": "Registration",
    "free_models_count": "2",
    "max_context": "128K",
    "modalities": "text",
    "best_models": [
      {
        "name": "deepseek-chat (V3.2)",
        "id": "deepseek-chat-v3-2",
        "context": "128K",
        "rate_limit": "Dynamic"
      },
      {
        "name": "deepseek-reasoner (R1)",
        "id": "deepseek-reasoner-r1",
        "context": "128K",
        "rate_limit": "Dynamic"
      }
    ]
  },
  {
    "provider": "Nscale",
    "base_url": "https://inference.api.nscale.com/v1",
    "key_url": "https://console.nscale.com/",
    "credit_card": "Registration",
    "free_models_count": "2",
    "max_context": "128K",
    "modalities": "text",
    "best_models": [
      {
        "name": "Llama-3.3-70B-Instruct",
        "id": "llama-3-3-70b-instruct",
        "context": "128K",
        "rate_limit": "Fair-use"
      },
      {
        "name": "DeepSeek-R1-Distill-Llama-70B",
        "id": "deepseek-r1-distill-llama-70b",
        "context": "128K",
        "rate_limit": "Fair-use"
      }
    ]
  },
  {
    "provider": "Nebius",
    "base_url": "https://api.studio.nebius.com/v1",
    "key_url": "https://studio.nebius.com/settings/api-keys",
    "credit_card": "Registration",
    "free_models_count": "1",
    "max_context": "128K",
    "modalities": "text",
    "best_models": [
      {
        "name": "Qwen3-235B-A22B",
        "id": "qwen3-235b-a22b",
        "context": "128K",
        "rate_limit": "Tier-based"
      }
    ]
  }
];
