import streamlit as st
import random
import os
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
# ===================== TESTE DE CONEXÃO GOOGLE SHEETS =====================
SHEET_ID = "1LuLxwskv_jrwOHTRmOKKeceI7WpzeTCIauCPUwhueUU"
SHEET_NAME = "Página1"

try:
    service_account_info = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(dict(service_account_info), scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    st.success(f"Conectado à planilha: {sh.title}")
    worksheet = sh.worksheet(SHEET_NAME)
    st.info(f"Conectado à worksheet: {worksheet.title}")
except Exception as e:
    st.error(f"Erro de conexão: {e}")

# ===================== FUNÇÃO DE SALVAR NO GOOGLE SHEETS =====================
def salvar_respostas_google_sheets(dados_demograficos, respostas):
    try:
        service_account_info = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(dict(service_account_info), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet(SHEET_NAME)
        for resp in respostas:
            linha = [
                dados_demograficos.get("idade", ""),
                dados_demograficos.get("sexo", ""),
                dados_demograficos.get("escolaridade", ""),
                dados_demograficos.get("cidade", ""),
                dados_demograficos.get("renda", ""),
                resp["video"],
                "; ".join(resp["opcoes"]),
                resp["resposta_usuario"],
                resp["resposta_certa"],
                "Sim" if resp["correta"] else "Não"
            ]
            worksheet.append_row(linha, value_input_option="USER_ENTERED")
        return True, ""
    except Exception as e:
        return False, str(e)

# ===================== FORMULÁRIO DEMOGRÁFICO =====================
if "formulario_preenchido" not in st.session_state:
    st.session_state.formulario_preenchido = False

if not st.session_state.formulario_preenchido:
    st.title("Formulário Demográfico - Teste Cambridge Mindreading")
    with st.form("demographic_form"):
        idade = st.number_input("Idade (em anos):", min_value=0, max_value=120, step=1, format="%d")
        sexo = st.radio("Sexo biológico:", options=["Masculino", "Feminino"])
        escolaridade = st.selectbox(
            "Grau de instrução:",
            options=[
                "Ensino Fundamental",
                "Ensino Médio",
                "Ensino Superior",
                "Pós-graduação"
            ]
        )
        cidade = st.text_input("Cidade/Estado de origem:")
        renda = st.selectbox(
            "Faixa de renda familiar mensal:",
            options=[
                "Até 1 salário mínimo",
                "1 a 3 salários mínimos",
                "3 a 5 salários mínimos",
                "5 a 10 salários mínimos",
                "Acima de 10 salários mínimos",
                "Prefiro não informar"
            ]
        )
        submit = st.form_submit_button("Iniciar teste")

    if submit:
        if idade and cidade.strip():
            st.session_state.formulario_preenchido = True
            st.session_state.dados_demograficos = {
                "idade": idade,
                "sexo": sexo,
                "escolaridade": escolaridade,
                "cidade": cidade,
                "renda": renda
            }
            st.success("Dados registrados com sucesso! O teste irá começar.")
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos obrigatórios antes de iniciar o teste.")
    else:
        st.info("Preencha todos os campos e clique em 'Iniciar teste' para começar.")

# ===================== TESTE PRINCIPAL =====================
if st.session_state.formulario_preenchido:
    st.title("Cambridge Mindreading Face Task – Versão Online (Português)")

    PASTA_VIDEOS = "videos"
    videos = [
        ("0101702M2Vresentful.mp4", ["Segura", "Amigável", "Magoada", "Atraente"], 3),
        ("0101702M3Vresentful.mp4", ["Cansado", "Magoado", "Desconcentrado", "Angustiado"], 2),
        ("0101702M8Vresentful.mp4", ["Confusa", "Modesta", "Magoada", "Piedosa"], 3),
        ("0110401M1Vstern.mp4", ["Sério", "Calculista", "Assertivo", "Falso"], 1),
        ("0110401M2Vstern.mp4", ["Angustiada", "Amigável", "Severa", "Rejeitada"], 3),
        ("0110401S5Vstern.mp4", ["Atormentado", "Resignado", "Furioso", "Sério"], 4),
        ("0201901S1Vgrave.mp4", ["Preocupado", "Desconcentrado", "Abandonado", "Resignado"], 1),
        ("0201901S6Vgrave.mp4", ["Crítica", "Conformada", "Preocupada", "Sedutora"], 3),
        ("0203501M4Vsubdued.mp4", ["Arrogante", "Desconcentrada", "Abatida", "Revigorada"], 3),
        ("0203501Y2Vsubdued.mp4", ["Apática", "Abatida", "Eufórica", "Preocupada"], 2),
        ("0305802M2Vexonerated.mp4", ["Aliviada", "Rejeitada", "Desconcentrada", "Abandonada"], 1),
        ("0305802S4Vexonerated.mp4", ["Esgotada", "Aterrorizada", "Aliviada", "Frustrada"], 3),
        ("0305802Y7Vexonerated.mp4", ["Emotivo", "Assertivo", "Sonhador", "Aliviado"], 4),
        ("0601901S2Vuneasy.mp4", ["Opressiva", "Enérgica", "Inquieta", "Apática"], 3),
        ("0601901S5Vuneasy.mp4", ["Acuado", "Despreocupado", "Inquieto", "Desnorteado"], 3),
        ("0703001M4Vempathic.mp4", ["Atenta", "Empática", "Séria", "Conformada"], 2),
        ("0703001S5Vempathic.mp4", ["Revigorado", "Conformado", "Bondoso", "Dissimulado"], 3),
        ("0703001Y2Vempathic.mp4", ["Emocionada", "Insegura", "Histérica", "Empática"], 4),
        ("0802202M8Vvibrant.mp4", ["Indiferente", "Atormentada", "Tensa", "Vibrante"], 4),
        ("0802202Y4Vvibrant.mp4", ["Apavorada", "Vibrante", "Empática", "Oprimida"], 2),
        ("0903302M1Vlured.mp4", ["Sério", "Comovido", "Sedutor", "Confuso"], 3),
        ("0903302M2Vlured.mp4", ["Sedutora", "Revigorada", "Impaciente", "Amargurada"], 1),
        ("0903302S2Vlured.mp4", ["Sedutora", "Indiferente", "Insegura", "Empática"], 1),
        ("0903001M4Vadmiring.mp4", ["Submissa", "Encantada", "Chateada", "Irritada"], 2),
        ("1004701M3Vsubservient.mp4", ["Tenso", "Desmotivado", "Submisso", "Amoroso"], 3),
        ("1004701Y1Vsubservient.mp4", ["Acuado", "Conformado", "Submisso", "Despreocupado"], 3),
        ("1101401M6Vappalled.mp4", ["Horrorizada", "Desatenta", "Sobrecarregada", "Acomodada"], 1),
        ("1101401S5Vappalled.mp4", ["Arrogante", "Submisso", "Impiedoso", "Horrorizado"], 4),
        ("1101401Y5Vappalled.mp4", ["Horrorizado", "Saudoso", "Retraído", "Cínico"], 1),
        ("1202701M2Vconfronted.mp4", ["Séria", "Agradecida", "Acareada", "Angustiada"], 3),
        ("1202701M8Vconfronted.mp4", ["Simpática", "Acareada", "Bondosa", "Acomodada"], 2),
        ("1202701Y2Vconfronted.mp4", ["Surpresa", "Elogiosa", "Tranquila", "Fria"], 1),
        ("1400901M2Vintimate.mp4", ["Atormentada", "Despreocupada", "Amorosa", "Insegura"], 3),
        ("1400901Y2Vintimate.mp4", ["Firme", "Amorosa", "Agitada", "Apreensiva"], 2),
        ("1700802M4Vinsincere.mp4", ["Desmotivada", "Falsa", "Chateada", "Fascinada"], 2),
        ("1700802Y7Vinsincere.mp4", ["Angustiado", "Contraditório", "Disperso", "Falso"], 4),
        ("1801301Y7Vrestless.mp4", ["Impiedoso", "Incomodado", "Atraente", "Inquieto"], 4),
        ("1900201M1Vuncertain.mp4", ["Submisso", "Inseguro", "Triunfante", "Atraente"], 2),
        ("1900201M6Vappealing.mp4", ["Agradecida", "Atraente", "Dispersa", "Falsa"], 2),
        ("2001001Y7Vmortified.mp4", ["Bondoso", "Desatento", "Envergonhado", "Assertivo"], 3),
        ("2001001Y8Vmortified.mp4", ["Cautelosa", "Entendiada", "Aflita", "Melancólica"], 3),
        ("2100102Y3Vguarded.mp4", ["Arrogante", "Oprimido", "Cauteloso", "Furioso"], 3),
        ("2100102Y8Vguarded.mp4", ["Submissa", "Cautelosa", "Desgostosa", "Angustiada"], 2),
        ("2200301M6Vdistaste.mp4", ["Ofendida", "Vigilante", "Menosprezo", "Acomodada"], 3),
        ("2200301M7Vdistaste.mp4", ["Admirado", "Menosprezo", "Provocado", "Distraído"], 2),
        ("2200301Y4Vdistaste.mp4", ["Lisonjeada", "Apática", "Menosprezo", "Confusa"], 3),
        ("2300501S2Vnostalgic.mp4", ["Aliviada", "Nostálgica", "Devastada", "Calculista"], 2),
        ("2300501S5Vnostalgic.mp4", ["Apreciando", "Julgando", "Histérico", "Nostálgico"], 4),
        ("2300501Y5Vnostalgic.mp4", ["Negligenciado", "Revigorado", "Nostálgico", "Oprimido"], 3),
        ("2402601M1Vreassured.mp4", ["Sedutor", "Apático", "Aliviado", "Saudosista"], 3),
        ("2402601M8Vreassured.mp4", ["Encantada", "Aliviada", "Atenta", "Desconectada"], 2),
        ("2402601S1Vreassured.mp4", ["Vigilante", "Aliviado", "Admirado", "Cauteloso"], 2)
    ]

    if "ordem" not in st.session_state:
        st.session_state.ordem = list(range(len(videos)))
        random.shuffle(st.session_state.ordem)

    if "respostas" not in st.session_state:
        st.session_state.respostas = []

    if "indice" not in st.session_state:
        st.session_state.indice = 0

    indice = st.session_state.indice

    if indice < len(videos):
        idx = st.session_state.ordem[indice]
        video, opcoes, correta = videos[idx]
        caminho = os.path.join(PASTA_VIDEOS, video)

        st.info(
            """
            Instruções da Tarefa:

            Você verá vídeos curtos de rostos de pessoas.
            Após cada vídeo, escolha a palavra que melhor representa o sentimento da pessoa naquele momento.
            Para isso, pressione o botão correspondente à palavra.

            ⚠️ Atenção: Os vídeos serão apresentados em ordem aleatória.
            """
        )

        st.markdown(f"**Vídeo {indice+1} de {len(videos)}**")
        st.video(caminho)
        escolha = st.radio(
            "Como a pessoa do vídeo está se sentindo?",
            opcoes,
            index=None,
            key=f"escolha_{indice}"
        )
        if st.button("Confirmar resposta", key=f"botao_{indice}") and escolha is not None:
            st.session_state.respostas.append({
                "video": video,
                "opcoes": opcoes,
                "resposta_usuario": escolha,
                "correta": (opcoes.index(escolha) + 1 == correta),
                "resposta_certa": opcoes[correta-1]
            })
            st.session_state.indice += 1
            st.rerun()
    else:
        st.success("Tarefa finalizada! Obrigado.")

        total = len(st.session_state.respostas)
        acertos = sum(1 for r in st.session_state.respostas if r["correta"])
        erros = total - acertos
        percent_acertos = 100 * acertos / total if total else 0
        percent_erros = 100 * erros / total if total else 0

        # ------ CLASSIFICAÇÃO ------
        if percent_erros <= 14:
            nivel = "Muito Baixo – normotípico (Não levanta problemas)"
            cor = "green"
        elif percent_erros <= 29:
            nivel = "Baixo – normotípico (Não levanta problemas)"
            cor = "green"
        elif percent_erros <= 70:
            nivel = "Médio – normotípico (Não deve levantar preocupações)"
            cor = "blue"
        elif percent_erros <= 85:
            nivel = "Alto – risco clínico (Limítrofe - Deve preocupar)"
            cor = "orange"
        else:
            nivel = "Muito Alto – perfil clínico (Indicação de problema significativo)"
            cor = "red"

        col1, col2 = st.columns(2)
        col1.metric("Total de vídeos", total)
        col1.metric("Acertos", acertos)
        col1.metric("Erros", erros)
        col2.metric("Percentual de acertos", f"{percent_acertos:.1f}%")
        col2.metric("Percentual de erros", f"{percent_erros:.1f}%")

        st.markdown("---")
        st.markdown(f"### **Classificação psicométrica:**")
        st.markdown(f"<span style='color:{cor}; font-size:1.4em'><b>{nivel}</b></span>", unsafe_allow_html=True)

        # ------ ANÁLISE INTERPRETATIVA DETALHADA ------
        if percent_erros <= 14:
            interpretacao = """
**Definição:**  
Desempenho muito superior no reconhecimento de emoções e estados mentais complexos, indicando habilidades sólidas para práticas de funcionamento social, como reciprocidade social, empatia, formação e manutenção de vínculos, compreensão de ironia e sarcasmo, e regulação emocional em contextos sociais.  
Não há qualquer indício de prejuízo clínico ou necessidade de preocupação quanto à competência para o reconhecimento de emoções complexas.

**Ação sugerida:**  
Nenhuma intervenção ou acompanhamento necessário.
"""
        elif percent_erros <= 29:
            interpretacao = """
**Definição:**  
Desempenho superior no reconhecimento de emoções e estados mentais complexos, indicando habilidades expressivas para práticas de funcionamento social, como reciprocidade social, empatia, formação e manutenção de vínculos, compreensão de ironia e sarcasmo, e regulação emocional em contextos sociais.  
Não há qualquer indício de prejuízo clínico ou necessidade de preocupação quanto à competência para o reconhecimento de emoções complexas.

**Ação sugerida:**  
Nenhuma intervenção ou acompanhamento necessário.
"""
        elif percent_erros <= 70:
            interpretacao = """
**Definição:**  
Desempenho dentro da média populacional, refletindo variação típica de reconhecimento de emoções e estados mentais complexos, indicando habilidades razoáveis para práticas de funcionamento social, como reciprocidade social, empatia, formação e manutenção de vínculos, compreensão de ironia e sarcasmo, e regulação emocional em contextos sociais.  
Não há qualquer indício de prejuízo clínico ou necessidade de preocupação quanto à competência para o reconhecimento de emoções complexas.

**Ação sugerida:**  
Nenhuma preocupação clínica. Manter rotina de desenvolvimento habitual.
"""
        elif percent_erros <= 85:
            interpretacao = """
**Definição:**  
Pontuação de erros elevada, situando-se em zona limítrofe, sugere risco clínico para dificuldades no reconhecimento de emoções e estados mentais complexos. Esse padrão pode estar associado a traços do espectro autista de alto funcionamento, especialmente àquelas manifestações mais sutis e compensadas na infância ou adolescência.  
Indica vulnerabilidades relevantes para práticas de funcionamento social, como empatia cognitiva, reciprocidade, compreensão de nuances sociais (ironia, sarcasmo) e regulação emocional diante de situações sociais.  
Pode refletir risco de isolamento, dificuldades na manutenção de vínculos e prejuízos adaptativos, mesmo em indivíduos com inteligência preservada e elevadas habilidades acadêmicas adequadas.

**Ação sugerida:**  
Recomenda-se observação clínica sistemática e investigação aprofundada do contexto funcional e histórico de desenvolvimento.  
É importante monitorar o impacto dessas dificuldades no cotidiano, promover intervenções preventivas (como treinamento de habilidades sociais) e considerar avaliação interdisciplinar quando houver outros indicadores de risco.
"""
        else:
            interpretacao = """
**Definição:**  
Pontuação de erros muito elevada, situada em faixa clínica, indica prejuízo expressivo e persistente no reconhecimento de emoções e estados mentais complexos.  
Esse perfil é fortemente sugestivo de quadros do espectro autista de alto funcionamento, nos quais as dificuldades sociais se manifestam de forma mais sutil, mas com impacto importante na qualidade das interações sociais, na construção e manutenção de vínculos afetivos, na compreensão de nuances sociais (como ironia, duplo sentido e sarcasmo) e na autorregulação emocional.  
Tais prejuízos tendem a comprometer a adaptação social e funcional, mesmo em indivíduos com desempenho intelectual preservado e boa escolaridade, podendo favorecer isolamento, mal-entendidos, sofrimento emocional e dificuldades de integração social.

**Ação sugerida:**  
Recomenda-se avaliação clínica detalhada e multidisciplinar, com foco em neurodesenvolvimento e habilidades sociais.  
Indica necessidade de intervenções específicas (como programas estruturados de habilidades sociais, psicoterapia focal ou treinamento em teoria da mente) e pode justificar encaminhamento para serviços especializados em autismo ou dificuldades socioemocionais, visando suporte individualizado e orientação para a rede de apoio da pessoa.
"""
        st.markdown("---")
        st.markdown("### **Análise Interpretativa Detalhada:**")
        st.markdown(interpretacao)

        # Botão para baixar o CSV detalhado
        df = pd.DataFrame(st.session_state.respostas)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar respostas detalhadas (CSV)", data=csv, file_name="respostas_cambridge.csv", mime='text/csv')

        # SALVAR NO GOOGLE SHEETS
        ok, msg = salvar_respostas_google_sheets(st.session_state.dados_demograficos, st.session_state.respostas)
        if ok:
            st.success("Respostas salvas no Google Sheets com sucesso!")
        else:
            st.warning(f"⚠️ Não foi possível salvar no Google Sheets: {msg}")
