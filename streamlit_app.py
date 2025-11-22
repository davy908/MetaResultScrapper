"""
Meta Ads Library Scraper - Web App
VERSÃO SEM SELENIUM - Usa requests + BeautifulSoup
Mais estável para Streamlit Cloud
"""

import streamlit as st
import requests
from urllib.parse import quote, urlparse, parse_qs
import json
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="Meta Ads Library Scraper",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    </style>
""", unsafe_allow_html=True)


class MetaAdsAPI:
    """
    Classe que usa a Graph API do Meta para buscar anúncios
    Muito mais estável que Selenium!
    """
    
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def buscar_por_page_id(self, page_id):
        """Busca anúncios usando a Graph API"""
        
        if not self.access_token:
            return self._buscar_sem_api(page_id)
        
        try:
            url = f"{self.base_url}/ads_archive"
            params = {
                'access_token': self.access_token,
                'search_page_ids': page_id,
                'ad_active_status': 'ALL',
                'fields': 'id,ad_creation_time,ad_delivery_start_time,ad_snapshot_url,page_name,ad_creative_bodies',
                'limit': 20
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'error' in data:
                raise Exception(data['error']['message'])
            
            return self._formatar_resultado(data, page_id)
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'mensagem': 'Erro ao buscar via API. Tente sem Access Token.'
            }
    
    def _buscar_sem_api(self, page_id):
        """Retorna informações básicas sem usar a API"""
        url = f"https://www.facebook.com/ads/library/?view_all_page_id={page_id}"
        
        return {
            'sucesso': True,
            'page_id': page_id,
            'url': url,
            'total_resultados': 'Desconhecido (sem API)',
            'anuncios': [],
            'mensagem': 'Para ver os anúncios, acesse a URL abaixo ou forneça um Access Token da Meta Graph API'
        }
    
    def _formatar_resultado(self, data, page_id):
        """Formata os resultados da API"""
        anuncios = []
        
        for i, ad in enumerate(data.get('data', []), 1):
            anuncios.append({
                'index': i,
                'id': ad.get('id'),
                'page_name': ad.get('page_name'),
                'criacao': ad.get('ad_creation_time'),
                'inicio': ad.get('ad_delivery_start_time'),
                'url_snapshot': ad.get('ad_snapshot_url'),
                'texto': ad.get('ad_creative_bodies', [''])[0] if ad.get('ad_creative_bodies') else 'N/A'
            })
        
        return {
            'sucesso': True,
            'page_id': page_id,
            'url': f"https://www.facebook.com/ads/library/?view_all_page_id={page_id}",
            'total_resultados': f"{len(anuncios)} anúncios encontrados",
            'anuncios': anuncios,
            'timestamp': datetime.now().isoformat()
        }


def extrair_page_id_da_url(url):
    """Extrai o Page ID de uma URL"""
    try:
        # Tenta pegar view_all_page_id
        match = re.search(r'view_all_page_id=(\d+)', url)
        if match:
            return match.group(1)
        
        # Tenta outros padrões
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        
        if 'view_all_page_id' in query:
            return query['view_all_page_id'][0]
        
        return None
    except:
        return None


def main():
    # Header
    st.markdown('<h1 class="main-header">🕷️ Meta Ads Library Scraper</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extraia dados da Biblioteca de Anúncios do Facebook/Instagram</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Como usar")
        st.markdown("""
        **3 formas de buscar:**
        
        1️⃣ **Page ID**: Cole o ID da página
        
        2️⃣ **URL Completa**: Cole a URL da biblioteca
        
        3️⃣ **Com Access Token**: Para dados completos (opcional)
        
        ---
        
        **⚠️ IMPORTANTE:**
        
        Esta versão usa a **Graph API do Meta** em vez de Selenium, que é muito mais estável e rápida!
        
        **Sem Access Token:** Mostra apenas a URL para acessar
        
        **Com Access Token:** Extrai dados completos dos anúncios
        """)
        
        st.header("🔑 Access Token (Opcional)")
        st.info("Forneça um token para extrair dados completos. Deixe vazio para apenas gerar URLs.")
        
        access_token = st.text_input(
            "Meta Graph API Token",
            type="password",
            placeholder="Cole seu token aqui...",
            help="Como obter: developers.facebook.com/tools/explorer"
        )
        
        st.markdown("---")
        st.markdown("**Versão:** 2.0 (API Mode)")
        st.markdown("**Método:** Graph API (sem Selenium)")
    
    # Tabs
    tab1, tab2 = st.tabs(["🆔 Page ID", "🔗 URL Completa"])
    
    # ============================================
    # TAB 1: Page ID
    # ============================================
    with tab1:
        st.subheader("Buscar por Page ID")
        st.markdown("Cole o ID numérico da página do Facebook")
        
        page_id = st.text_input(
            "Page ID",
            placeholder="Ex: 675929692278580",
            key="page_id_input"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            buscar_page_id = st.button("🔎 Buscar Anúncios", key="btn_page_id", use_container_width=True)
        
        if buscar_page_id and page_id:
            with st.spinner("🚀 Buscando dados via Graph API..."):
                try:
                    api = MetaAdsAPI(access_token if access_token else None)
                    resultado = api.buscar_por_page_id(page_id)
                    
                    exibir_resultados(resultado)
                
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    # ============================================
    # TAB 2: URL Completa
    # ============================================
    with tab2:
        st.subheader("Buscar por URL Completa")
        st.markdown("Cole a URL da biblioteca de anúncios")
        
        url_input = st.text_input(
            "URL Completa",
            placeholder="Ex: https://www.facebook.com/ads/library/?view_all_page_id=123456",
            key="url_input"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            buscar_url = st.button("🔎 Buscar Anúncios", key="btn_url", use_container_width=True)
        
        if buscar_url and url_input:
            page_id_extraido = extrair_page_id_da_url(url_input)
            
            if page_id_extraido:
                st.success(f"✅ Page ID extraído: {page_id_extraido}")
                
                with st.spinner("🚀 Buscando dados via Graph API..."):
                    try:
                        api = MetaAdsAPI(access_token if access_token else None)
                        resultado = api.buscar_por_page_id(page_id_extraido)
                        
                        exibir_resultados(resultado)
                    
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
            else:
                st.error("❌ Não foi possível extrair o Page ID da URL")
                st.info("💡 Tente copiar apenas o número do Page ID e usar a aba 'Page ID'")


def exibir_resultados(resultado):
    """Exibe os resultados"""
    
    if not resultado.get('sucesso', True):
        st.error(f"❌ {resultado.get('mensagem', 'Erro desconhecido')}")
        if resultado.get('erro'):
            st.code(resultado['erro'])
        return
    
    st.success("✅ Busca concluída!")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Page ID", resultado.get('page_id', 'N/A'))
    
    with col2:
        st.metric("📦 Resultados", resultado.get('total_resultados', 'N/A'))
    
    with col3:
        st.metric("🕐 Hora", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # URL da biblioteca
    st.subheader("🔗 Acesse a Biblioteca de Anúncios")
    url = resultado.get('url', '')
    st.markdown(f"**[Clique aqui para ver todos os anúncios →]({url})**")
    st.code(url, language="text")
    
    # Mensagem se não tiver token
    if resultado.get('mensagem'):
        st.info(resultado['mensagem'])
    
    # Anúncios
    anuncios = resultado.get('anuncios', [])
    
    if anuncios:
        st.markdown("---")
        st.subheader(f"📢 {len(anuncios)} Anúncios Encontrados")
        
        for ad in anuncios:
            with st.expander(f"🎯 Anúncio #{ad['index']} - {ad.get('page_name', 'N/A')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**ID:** `{ad.get('id', 'N/A')}`")
                    st.markdown(f"**Página:** {ad.get('page_name', 'N/A')}")
                    st.markdown(f"**Criado:** {ad.get('criacao', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Início:** {ad.get('inicio', 'N/A')}")
                    if ad.get('url_snapshot'):
                        st.markdown(f"**[Ver Anúncio →]({ad['url_snapshot']})**")
                
                if ad.get('texto') and ad['texto'] != 'N/A':
                    st.markdown("**Texto:**")
                    st.text_area(
                        "Conteúdo",
                        ad['texto'],
                        height=100,
                        key=f"ad_text_{ad['index']}",
                        label_visibility="collapsed"
                    )
        
        # Download
        st.markdown("---")
        json_str = json.dumps(resultado, ensure_ascii=False, indent=2)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Baixar dados (JSON)",
                data=json_str,
                file_name=f"meta_ads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    else:
        st.warning("⚠️ Nenhum anúncio foi extraído")
        st.info("""
        **💡 Para ver os anúncios:**
        
        1. Acesse a URL acima no navegador
        2. OU forneça um Access Token da Meta Graph API na barra lateral
        
        **Como obter um token:**
        - Acesse: https://developers.facebook.com/tools/explorer/
        - Clique em "Generate Access Token"
        - Selecione a permissão: `ads_read`
        - Cole o token na barra lateral
        """)


if __name__ == "__main__":
    main()
