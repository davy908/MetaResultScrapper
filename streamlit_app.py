"""
Meta Ads Library Scraper - Web App
Versão CORRIGIDA com Selenium usando Chromium do sistema
"""

import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Meta Ads Library Scraper",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

options.binary_location = '/usr/bin/chromium'
service = Service(executable_path='/usr/bin/chromedriver')

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


@st.cache_resource
def get_driver():
    """
    Inicializa o ChromeDriver usando Chromium do sistema (Streamlit Cloud)
    Cache para reutilizar o mesmo driver
    """
    options = Options()
    
    # Configurações essenciais para Streamlit Cloud
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Configurações de performance
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')  # Para páginas estáticas
    
    # IMPORTANTE: Usar Chromium do sistema (instalado via apt.txt)
    options.binary_location = '/usr/bin/chromium'
    
    try:
        # Usa o chromedriver do sistema (instalado via apt.txt)
        service = Service(executable_path='/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        return driver
    
    except Exception as e:
        st.error(f"""
        ❌ Erro ao iniciar Chrome/Chromium: {str(e)}
        
        **Verifique:**
        1. Arquivo `packages.txt` existe com:
           ```
           chromium
           chromium-chromedriver
           ```
        
        2. OU arquivo `apt.txt` existe com:
           ```
           chromium
           chromium-chromedriver
           ```
        """)
        return None


class MetaAdsScraper:
    """Classe do scraper usando Selenium"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15) if driver else None
    
    def buscar_por_url(self, url):
        """Busca por URL completa"""
        if not self.driver:
            return None
        
        # Extrai Page ID se existir
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
        if not self.driver:
            return None
        
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id={page_id}"
        self.driver.get(url)
        time.sleep(5)
        return self._extrair_dados()
    
    def buscar_por_termo(self, termo, country='BR'):
        """Busca por termo"""
        if not self.driver:
            return None
        
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
        
        # Extrai total de resultados
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
            
            for i, card in enumerate(cards[:20]):
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


def main():
    # Header
    st.markdown('<h1 class="main-header">🕷️ Meta Ads Library Scraper</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extraia dados da Biblioteca de Anúncios do Facebook/Instagram</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Como usar")
        st.markdown("""
        **3 formas de buscar:**
        
        1️⃣ **Page ID**: Cole o ID numérico da página
        
        2️⃣ **URL Completa**: Cole a URL da biblioteca
        
        3️⃣ **Termo de Busca**: Busque por palavra-chave
        
        ---
        
        **Dicas:**
        - A primeira busca pode demorar (inicia o navegador)
        - Page ID é o mais rápido
        - Máximo de 20 anúncios por busca
        """)
        
        st.header("ℹ️ Sobre")
        st.info("Ferramenta para extrair dados públicos da Biblioteca de Anúncios Meta/Facebook")
        
        st.markdown("---")
        st.markdown("**Versão:** 2.0 (Selenium + Chromium)")
    
    # Inicializa o driver (apenas uma vez graças ao cache)
    driver = get_driver()
    
    if not driver:
        st.error("❌ Não foi possível iniciar o navegador. Verifique a configuração do Chromium.")
        st.stop()
    
    scraper = MetaAdsScraper(driver)
    
    # Tabs
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
            with st.spinner("🚀 Buscando dados com Selenium..."):
                try:
                    dados = scraper.buscar_por_page_id(page_id)
                    if dados:
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
            with st.spinner("🚀 Processando URL..."):
                try:
                    dados = scraper.buscar_por_url(url)
                    if dados:
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
                    dados = scraper.buscar_por_termo(termo, country)
                    if dados:
                        exibir_resultados(dados)
                except Exception as e:
                    st.error(f"❌ Erro: {e}")


def exibir_resultados(dados):
    """Exibe os resultados"""
    st.success("✅ Busca concluída!")
    
    # Métricas
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
        
        # Download
        st.markdown("---")
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
