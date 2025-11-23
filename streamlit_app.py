"""
Meta Ads Library Scraper - Web App
Versão REFATORADA com estrutura correta da página do Facebook
"""

import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
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
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_driver():
    """
    Inicializa o ChromeDriver com configurações otimizadas
    """
    options = Options()
    
    # Configurações essenciais
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # User agent realista
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Configuração de janela
    options.add_argument('--window-size=1920,1080')
    
    # Usar Chromium do sistema
    options.binary_location = '/usr/bin/chromium'
    
    try:
        service = Service(executable_path='/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        st.error(f"❌ Erro ao iniciar Chrome: {str(e)}")
        return None


class MetaAdsScraper:
    """
    Scraper refatorado com estrutura correta do Facebook Ads Library
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20) if driver else None
    
    def buscar_por_page_id(self, page_id):
        """Busca APENAS o total de resultados - rápido!"""
        if not self.driver:
            return None
        
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id={page_id}"
        
        try:
            self.driver.get(url)
            
            # Aguarda apenas 5 segundos - só precisamos do total!
            time.sleep(5)
            
            # Extrai APENAS o total
            total = self._extrair_total_resultados()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'total_resultados': total
            }
        
        except Exception as e:
            return {
                'erro': str(e),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def buscar_por_url(self, url):
        """Busca por URL completa - APENAS total"""
        if not self.driver:
            return None
        
        # Extrai Page ID da URL
        match = re.search(r'view_all_page_id=(\d+)', url)
        if match:
            return self.buscar_por_page_id(match.group(1))
        
        # Ou usa a URL diretamente
        try:
            self.driver.get(url)
            time.sleep(5)
            
            total = self._extrair_total_resultados()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'total_resultados': total
            }
        except Exception as e:
            return {
                'erro': str(e),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def _extrair_total_resultados(self):
        """
        Extrai APENAS o número total de resultados
        Exemplo: "~1 result" ou "36 results"
        """
        try:
            # O seletor que você mencionou - funciona!
            selectors = [
                "div.x8t9es0.x1uxerd5.xrohxju.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli",
                "div[role='heading'][aria-level='3']"
            ]
            
            for selector in selectors:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elementos:
                        texto = elem.text.strip()
                        # Procura por "X result" ou "X resultados"
                        if 'result' in texto.lower() or 'anúnc' in texto.lower():
                            return texto
                except:
                    continue
            
            return "Não encontrado"
        
        except Exception as e:
            return f"Erro: {str(e)}"


def main():
    # Header
    st.markdown('<h1 class="main-header">🕷️ Meta Ads Library Scraper</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Extraia dados da Biblioteca de Anúncios do Facebook/Instagram</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Como usar")
        st.markdown("""
        **2 formas de buscar:**
        
        1️⃣ **Page ID**: Cole o ID numérico da página
        
        2️⃣ **URL Completa**: Cole a URL completa da biblioteca
        
        ---
        
        **⚠️ Importante:**
        - Tempo de busca: ~5 segundos
        - Extrai APENAS o total de resultados
        - Rápido e objetivo!
        """)
        
        st.markdown("---")
        st.markdown("**Versão:** 3.0 (Refatorada)")
    
    # Inicializa driver
    driver = get_driver()
    
    if not driver:
        st.error("❌ Não foi possível iniciar o navegador")
        st.stop()
    
    scraper = MetaAdsScraper(driver)
    
    # Tabs
    tab1, tab2 = st.tabs(["🆔 Page ID", "🔗 URL Completa"])
    
    # TAB 1: Page ID
    with tab1:
        st.subheader("Buscar por Page ID")
        
        page_id = st.text_input(
            "Page ID",
            placeholder="Ex: 675929692278580",
            key="page_id_input"
        )
        
        if st.button("🔎 Buscar Anúncios", key="btn_page_id"):
            if page_id:
                with st.spinner("🚀 Extraindo total de resultados... (~5 segundos)"):
                    dados = scraper.buscar_por_page_id(page_id)
                    if dados:
                        exibir_resultados(dados)
            else:
                st.warning("⚠️ Digite um Page ID")
    
    # TAB 2: URL Completa
    with tab2:
        st.subheader("Buscar por URL Completa")
        
        url = st.text_input(
            "URL Completa",
            placeholder="Ex: https://www.facebook.com/ads/library/?view_all_page_id=123456",
            key="url_input"
        )
        
        if st.button("🔎 Buscar Anúncios", key="btn_url"):
            if url:
                with st.spinner("🚀 Extraindo total de resultados..."):
                    dados = scraper.buscar_por_url(url)
                    if dados:
                        exibir_resultados(dados)
            else:
                st.warning("⚠️ Cole uma URL")


def exibir_resultados(dados):
    """Exibe APENAS o total de resultados - limpo e simples"""
    
    if 'erro' in dados:
        st.error(f"❌ Erro: {dados['erro']}")
        return
    
    st.success("✅ Extração concluída!")
    
    # APENAS O TOTAL - centralizado e grande
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
            <h1 style="font-size: 4rem; margin: 0; font-weight: bold;">{dados.get('total_resultados', 'N/A')}</h1>
            <p style="font-size: 1.5rem; margin-top: 1rem; opacity: 0.9;">Total de Anúncios</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Link para ver no Facebook
    st.info(f"**🔗 Ver anúncios no Facebook:** [Clique aqui]({dados.get('url', '#')})")
    
    # Download simples dos dados
    json_str = json.dumps(dados, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="📥 Baixar dados (JSON)",
        data=json_str,
        file_name=f"meta_ads_total_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


if __name__ == "__main__":
    main()
