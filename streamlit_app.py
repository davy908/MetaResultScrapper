"""
Meta Ads Library Scraper - Web App
Interface web bonita e fácil de usar com Streamlit
VERSÃO CORRIGIDA PARA STREAMLIT CLOUD
"""

import streamlit as st
import time
import json
from datetime import datetime
import pandas as pd

# Importações do Selenium dentro de try/except
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    st.error("⚠️ Selenium não disponível. Instale com: pip install selenium webdriver-manager")


# Configuração da página
st.set_page_config(
    page_title="Meta Ads Library Scraper",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS customizado para deixar bonito
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
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


class MetaAdsScraper:
    """Classe do scraper adaptada para Streamlit"""
    
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium não está instalado. Verifique requirements.txt")
        self.driver = None
        self.wait = None
    
    def iniciar_navegador(self):
        """Inicializa o navegador (headless para servidor)"""
        if self.driver:
            return
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        
        # Para Streamlit Cloud (usa chromium-browser)
        options.binary_location = '/usr/bin/chromium-browser'
        
        try:
            # Tenta usar o chromedriver do sistema primeiro (Streamlit Cloud)
            try:
                service = Service('/usr/bin/chromedriver')
                self.driver = webdriver.Chrome(service=service, options=options)
            except:
                # Fallback: usa webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            self.wait = WebDriverWait(self.driver, 15)
        except Exception as e:
            raise Exception(f"Erro ao iniciar navegador: {e}\n\nCertifique-se de que o arquivo apt.txt está presente com chromium-browser e chromium-chromedriver")
    
    def buscar_por_url(self, url):
        """Busca por URL completa"""
        if "view_all_page_id=" in url:
            import re
            match = re.search(r'view_all_page_id=(\d+)', url)
            if match:
                page_id = match.group(1)
                return self.buscar_por_page_id(page_id)
        
        self.driver.get(url)
        time.sleep(5)
        return self._extrair_dados()
    
    def buscar_por_page_id(self, page_id):
        """Busca por Page ID"""
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id={page_id}"
        self.driver.get(url)
        time.sleep(5)
        return self._extrair_dados()
    
    def buscar_por_termo(self, termo, country='BR'):
        """Busca por termo"""
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={termo}"
        self.driver.get(url)
        time.sleep(5)
        return self._extrair_dados()
    
    def _extrair_dados(self):
        """Extrai dados da página"""
        dados = {
            'timestamp': datetime.now().isoformat(),
            'url': self.driver.current_url,
            'total_resultados': None,
            'anuncios': []
        }
        
        # Extrai total
        try:
            elemento = self.driver.find_element(
                By.CSS_SELECTOR, 
                "div[role='heading'][aria-level='3']"
            )
            dados['total_resultados'] = elemento.text
        except:
            dados['total_resultados'] = "Não encontrado"
        
        # Rola a página
        self._scroll_page(scrolls=3)
        
        # Extrai anúncios
        try:
            cards = self.driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet]")
            
            for i, card in enumerate(cards[:20]):  # Pega até 20
                try:
                    texto = card.text
                    if texto and len(texto) > 50:
                        dados['anuncios'].append({
                            'index': i + 1,
                            'texto': texto[:500]
                        })
                except:
                    continue
        except Exception as e:
            pass
        
        return dados
    
    def _scroll_page(self, scrolls=5, delay=2):
        """Rola a página"""
        for i in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            self.driver = None


# ============================================
# INTERFACE STREAMLIT
# ============================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🕷️ Meta Ads Library Scraper</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extraia dados da Biblioteca de Anúncios do Facebook/Instagram</p>', unsafe_allow_html=True)
    
    # Sidebar com instruções
    with st.sidebar:
        st.header("📋 Como usar")
        st.markdown("""
        **3 formas de buscar:**
        
        1️⃣ **Page ID**: Cole o ID numérico da página
        
        2️⃣ **URL Completa**: Cole a URL da biblioteca
        
        3️⃣ **Termo de busca**: Busque por palavra-chave
        
        ---
        
        **Dicas:**
        - A primeira busca pode demorar (inicia o navegador)
        - Busque por Page ID é o mais rápido
        - Máximo de 20 anúncios por busca
        """)
        
        st.header("ℹ️ Sobre")
        st.info("Ferramenta para extrair dados públicos da Biblioteca de Anúncios Meta/Facebook")
        
        st.markdown("---")
        st.markdown("**Versão:** 1.0")
        st.markdown("**Desenvolvido com:** Python + Selenium + Streamlit")
    
    # Tabs para os 3 modos de busca
    tab1, tab2, tab3 = st.tabs(["🆔 Page ID", "🔗 URL Completa", "🔍 Termo de Busca"])
    
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
            with st.spinner("🚀 Iniciando navegador e buscando dados..."):
                try:
                    scraper = MetaAdsScraper()
                    scraper.iniciar_navegador()
                    
                    dados = scraper.buscar_por_page_id(page_id)
                    scraper.fechar()
                    
                    exibir_resultados(dados)
                
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    # ============================================
    # TAB 2: URL Completa
    # ============================================
    with tab2:
        st.subheader("Buscar por URL Completa")
        st.markdown("Cole a URL completa da biblioteca de anúncios")
        
        url = st.text_input(
            "URL Completa",
            placeholder="Ex: https://www.facebook.com/ads/library/?view_all_page_id=123456",
            key="url_input"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            buscar_url = st.button("🔎 Buscar Anúncios", key="btn_url", use_container_width=True)
        
        if buscar_url and url:
            with st.spinner("🚀 Processando URL e buscando dados..."):
                try:
                    scraper = MetaAdsScraper()
                    scraper.iniciar_navegador()
                    
                    dados = scraper.buscar_por_url(url)
                    scraper.fechar()
                    
                    exibir_resultados(dados)
                
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    # ============================================
    # TAB 3: Termo de Busca
    # ============================================
    with tab3:
        st.subheader("Buscar por Termo")
        st.markdown("Busque anúncios por palavra-chave")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            termo = st.text_input(
                "Termo de busca",
                placeholder="Ex: Fé e Jogos",
                key="termo_input"
            )
        
        with col2:
            country = st.selectbox(
                "País",
                ["BR", "US", "PT", "ES", "AR", "MX"],
                key="country_select"
            )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            buscar_termo = st.button("🔎 Buscar Anúncios", key="btn_termo", use_container_width=True)
        
        if buscar_termo and termo:
            with st.spinner(f"🚀 Buscando '{termo}' em {country}..."):
                try:
                    scraper = MetaAdsScraper()
                    scraper.iniciar_navegador()
                    
                    dados = scraper.buscar_por_termo(termo, country)
                    scraper.fechar()
                    
                    exibir_resultados(dados)
                
                except Exception as e:
                    st.error(f"❌ Erro: {e}")


def exibir_resultados(dados):
    """Exibe os resultados de forma bonita"""
    st.success("✅ Busca concluída!")
    
    # Métricas em cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total de Resultados", dados.get('total_resultados', 'N/A'))
    
    with col2:
        st.metric("📦 Anúncios Extraídos", len(dados.get('anuncios', [])))
    
    with col3:
        st.metric("🕐 Timestamp", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # URL da busca
    with st.expander("🔗 URL da busca"):
        st.code(dados.get('url', 'N/A'))
    
    # Anúncios
    if dados.get('anuncios'):
        st.subheader("📢 Anúncios Encontrados")
        
        for ad in dados['anuncios']:
            with st.expander(f"Anúncio #{ad['index']}"):
                st.text_area(
                    "Conteúdo",
                    ad['texto'],
                    height=150,
                    key=f"ad_{ad['index']}"
                )
        
        # Botão de download
        st.markdown("---")
        
        # Converte para JSON
        json_str = json.dumps(dados, ensure_ascii=False, indent=2)
        
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
        st.warning("⚠️ Nenhum anúncio foi extraído. Tente ajustar a busca.")


if __name__ == "__main__":
    main()
