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
        """Busca anúncios de uma página específica"""
        if not self.driver:
            return None
        
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id={page_id}"
        
        try:
            self.driver.get(url)
            
            # Aguarda a página carregar completamente
            time.sleep(10)
            
            return self._extrair_dados()
        
        except Exception as e:
            return {
                'erro': str(e),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def buscar_por_url(self, url):
        """Busca por URL completa"""
        if not self.driver:
            return None
        
        # Extrai Page ID da URL
        match = re.search(r'view_all_page_id=(\d+)', url)
        if match:
            return self.buscar_por_page_id(match.group(1))
        
        # Ou usa a URL diretamente
        try:
            self.driver.get(url)
            time.sleep(10)
            return self._extrair_dados()
        except Exception as e:
            return {
                'erro': str(e),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def _extrair_dados(self):
        """
        Extrai dados da página do Facebook Ads Library
        Baseado na estrutura real da página
        """
        dados = {
            'timestamp': datetime.now().isoformat(),
            'url': self.driver.current_url,
            'total_resultados': None,
            'anuncios': []
        }
        
        # 1. Extrair contagem total de resultados
        # A contagem geralmente está em um heading com texto tipo "123 results"
        dados['total_resultados'] = self._extrair_total_resultados()
        
        # 2. Scroll para carregar os anúncios
        self._scroll_progressivo(scrolls=5)
        
        # 3. Extrair cards de anúncios
        dados['anuncios'] = self._extrair_anuncios()
        
        return dados
    
    def _extrair_total_resultados(self):
        """
        Extrai o número total de resultados
        Exemplo: "34 results" ou "34 resultados"
        """
        try:
            # Tenta encontrar o elemento com a contagem
            # Baseado na sua observação: classe específica com aria-level="3"
            selectors = [
                "div.x8t9es0.x1uxerd5.xrohxju.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli",
                "div[role='heading'][aria-level='3']",
                "h3",
                "[class*='result']"
            ]
            
            for selector in selectors:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elementos:
                        texto = elem.text.strip()
                        # Procura por texto que contenha números + "result" ou similar
                        if re.search(r'\d+\s*(result|anúnc|ad)', texto, re.IGNORECASE):
                            return texto
                except:
                    continue
            
            # Se não encontrou, procura por qualquer texto com "result"
            try:
                elementos = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'result') or contains(text(), 'anúnc')]")
                for elem in elementos[:5]:
                    texto = elem.text.strip()
                    if any(char.isdigit() for char in texto):
                        return texto
            except:
                pass
            
            return "Não encontrado"
        
        except Exception as e:
            return f"Erro: {str(e)}"
    
    def _extrair_anuncios(self):
        """
        Extrai cards de anúncios individuais
        Cada anúncio no Facebook Ads Library tem uma estrutura específica
        """
        anuncios = []
        
        try:
            # O Facebook usa estruturas dinâmicas
            # Vamos procurar por padrões comuns de cards de anúncios
            
            # Estratégia 1: Procurar por links de snapshot de anúncios
            # Cada anúncio tem um link único para ver detalhes
            ad_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='ad_library_id']")
            
            if ad_links:
                st.info(f"Encontrados {len(ad_links)} links de anúncios")
                
                # Para cada link, pega o container pai que deve ter o conteúdo do anúncio
                for idx, link in enumerate(ad_links[:30]):  # Limita a 30
                    try:
                        # Pega o container do anúncio (geralmente vários níveis acima)
                        ad_container = link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'x1y1aw1k') or contains(@class, 'x1n2onr6')]")
                        
                        # Extrai informações
                        ad_id = re.search(r'ad_library_id=(\d+)', link.get_attribute('href'))
                        ad_id = ad_id.group(1) if ad_id else f"unknown_{idx}"
                        
                        # Texto do anúncio
                        texto_completo = ad_container.text
                        
                        anuncios.append({
                            'index': idx + 1,
                            'ad_id': ad_id,
                            'url': link.get_attribute('href'),
                            'texto': texto_completo[:1000] if texto_completo else "Sem texto"
                        })
                    
                    except Exception as e:
                        continue
            
            # Estratégia 2: Se não encontrou com links, tenta por estrutura de card
            if len(anuncios) == 0:
                # Procura por divs que parecem ser cards de anúncios
                possible_cards = self.driver.find_elements(By.CSS_SELECTOR, 
                    "div[class*='x1y1aw1k'], div[class*='x1n2onr6'], div[data-pagelet]")
                
                for idx, card in enumerate(possible_cards[:30]):
                    try:
                        texto = card.text.strip()
                        # Filtra cards que parecem ter conteúdo de anúncio
                        if texto and len(texto) > 50 and 'cookie' not in texto.lower():
                            anuncios.append({
                                'index': idx + 1,
                                'ad_id': f'card_{idx}',
                                'texto': texto[:1000]
                            })
                    except:
                        continue
        
        except Exception as e:
            st.error(f"Erro ao extrair anúncios: {str(e)}")
        
        return anuncios
    
    def _scroll_progressivo(self, scrolls=5):
        """
        Scroll progressivo para carregar conteúdo dinâmico
        """
        for i in range(scrolls):
            try:
                # Scroll até o final da página
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Scroll um pouco para cima para triggar lazy loading
                self.driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(1)
            except:
                break


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
        - Primeira busca pode demorar ~15 segundos
        - Extrai até 30 anúncios por busca
        - Funciona melhor com páginas ativas
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
                with st.spinner("🚀 Acessando página e extraindo dados... (pode levar até 20 segundos)"):
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
                with st.spinner("🚀 Processando URL..."):
                    dados = scraper.buscar_por_url(url)
                    if dados:
                        exibir_resultados(dados)
            else:
                st.warning("⚠️ Cole uma URL")


def exibir_resultados(dados):
    """Exibe os resultados de forma clara"""
    
    if 'erro' in dados:
        st.error(f"❌ Erro: {dados['erro']}")
        return
    
    st.success("✅ Extração concluída!")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total", dados.get('total_resultados', 'N/A'))
    
    with col2:
        st.metric("📦 Extraídos", len(dados.get('anuncios', [])))
    
    with col3:
        st.metric("🕐 Hora", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # URL
    with st.expander("🔗 URL acessada"):
        st.code(dados.get('url', 'N/A'))
    
    # Anúncios
    anuncios = dados.get('anuncios', [])
    
    if anuncios:
        st.subheader(f"📢 {len(anuncios)} Anúncios Encontrados")
        
        for ad in anuncios:
            with st.expander(f"Anúncio #{ad['index']} - ID: {ad.get('ad_id', 'N/A')}"):
                if 'url' in ad:
                    st.markdown(f"**[Ver anúncio no Facebook →]({ad['url']})**")
                st.text_area(
                    "Conteúdo",
                    ad['texto'],
                    height=200,
                    key=f"ad_{ad['index']}"
                )
        
        # Download
        st.markdown("---")
        json_str = json.dumps(dados, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📥 Baixar todos os dados (JSON)",
            data=json_str,
            file_name=f"meta_ads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        st.warning("⚠️ Nenhum anúncio foi extraído")
        st.info("""
        **Possíveis causas:**
        - A página não tem anúncios ativos
        - O Page ID está incorreto
        - A página não carregou completamente (tente novamente)
        - Estrutura do Facebook mudou (entre em contato)
        """)


if __name__ == "__main__":
    main()
