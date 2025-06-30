from datetime import datetime
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()


## conexão com a LLM
id_model = "llama3-70b-8192"
llm = ChatGroq(
    model=id_model,
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

## função de geração
def llm_generate(llm, prompt):
  template = ChatPromptTemplate.from_messages([
      ("system", "Você é um especialista em marketing digital com foco em SEO e escrita persuasiva."),
      ("human", "{prompt}"),
  ])

  chain = template | llm | StrOutputParser()

  res = chain.invoke({"prompt": prompt})
  return res

st.set_page_config(page_title = "Gerador de conteúdo 🤖", page_icon="🤖")
st.title("Gerador de conteúdo")

if 'historico' not in st.session_state:
    st.session_state.historico = []

# Campos do formulário
topic = st.text_input("Tema:", placeholder="Ex: saúde mental, alimentação saudável, prevenção, etc.")
platform = st.selectbox("Plataforma:", ['Instagram', 'Facebook', 'LinkedIn', 'Blog', 'E-mail'])
tone = st.selectbox("Tom:", ['Normal', 'Informativo', 'Inspirador', 'Urgente', 'Informal'])
length = st.selectbox("Tamanho:", ['Curto', 'Médio', 'Longo'])
audience = st.selectbox("Público-alvo:", ['Geral', 'Jovens adultos', 'Famílias', 'Idosos', 'Adolescentes'])
cta = st.checkbox("Incluir CTA")
hashtags = st.checkbox("Retornar Hashtags")
keywords = st.text_area("Palavras-chave (SEO):", placeholder="Ex: bem-estar, medicina preventiva...")

if st.button("Gerar conteúdo"):
    prompt = f"""
    Escreva um texto com SEO otimizado sobre o tema '{topic}'.
    Retorne em sua resposta apenas o texto final e não inclua ela dentro de aspas.
    - Onde será publicado: {platform}.
    - Tom: {tone}.
    - Público-alvo: {audience}.
    - Comprimento: {length}.
    - {"Inclua uma chamada para ação clara." if cta else "Não inclua chamada para ação"}
    - {"Retorne ao final do texto hashtags relevantes." if hashtags else "Não inclua hashtags."}
    {"- Palavras-chave que devem estar presentes nesse texto (para SEO): " + keywords if keywords else ""}
    """
    try:
        res = llm_generate(llm, prompt)

        # Exibe o texto em um campo copiável
        st.success("✅ Conteúdo gerado com sucesso!")
        st.text_area("📝 Conteúdo gerado:", value=res, height=300, key="conteudo_gerado")

        # (Opcional) Botão "copiar para área de transferência" usando o extra
        try:
            from streamlit_extras.st_copy_to_clipboard import st_copy_to_clipboard
            st_copy_to_clipboard(res, "📋 Copiar texto gerado")
        except ImportError:
            st.info("💡 Dica: instale `streamlit-extras` para ativar o botão copiar automaticamente.")

        # Adiciona ao histórico
        st.session_state.historico.append({
            "tema": topic,
            "plataforma": platform,
            "tom": tone,
            "público": audience,
            "tamanho": length,
            "texto": res,
        })

    except Exception as e:
        st.error(f"Erro: {e}")


st.markdown("---")
st.subheader("📚 Histórico de conteúdos gerados")

if st.session_state.historico:
    for i, item in enumerate(reversed(st.session_state.historico), 1):
        with st.expander(f"{i}. {item['tema']} ({item['plataforma']})"):
            st.markdown(f"**Tom:** {item['tom']}")
            st.markdown(f"**Público-alvo:** {item['público']}")
            st.markdown(f"**Tamanho:** {item['tamanho']}")
            st.markdown("**Texto gerado:**")
            st.markdown(item['texto'])
else:
    st.info("Nenhum conteúdo gerado ainda.")
