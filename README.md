# MetaResultScrapper

> Extraia dados públicos da Biblioteca de Anúncios do Facebook/Instagram com interface web moderna e intuitiva.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seu-app.streamlit.app)

---

## 🎯 Funcionalidades

- ✅ **3 modos de busca**: Page ID, URL completa ou termo de busca
- ✅ **Interface web bonita**: Sem instalação, funciona no navegador
- ✅ **Download em JSON**: Exporte os dados coletados
- ✅ **Totalmente gratuito**: Hospedagem no Streamlit Cloud
- ✅ **Responsivo**: Funciona em desktop e mobile

---

## 🚀 Acesso Rápido

**App em produção:** [seu-app.streamlit.app](https://seu-app.streamlit.app)

---

## 📋 Como Usar

### **Opção 1: Buscar por Page ID**
1. Cole o ID numérico da página
2. Exemplo: `675929692278580`
3. Clique em "Buscar Anúncios"

### **Opção 2: Buscar por URL Completa**
1. Cole a URL da biblioteca de anúncios
2. Exemplo: `https://www.facebook.com/ads/library/?view_all_page_id=123456`
3. Clique em "Buscar Anúncios"

### **Opção 3: Buscar por Termo**
1. Digite uma palavra-chave
2. Escolha o país
3. Clique em "Buscar Anúncios"

---

## 🛠️ Tecnologias

- **Python 3.11**
- **Streamlit** - Framework web
- **Selenium** - Automação do navegador
- **WebDriver Manager** - Gerenciamento automático do ChromeDriver

---

## 💻 Rodar Localmente

### **1. Clonar o repositório**
```bash
git clone https://github.com/davy908/MetaResultScrapper.git
cd MetaResultScrapper
```

### **2. Instalar dependências**
```bash
pip install -r requirements.txt
```

### **3. Rodar o app**
```bash
streamlit run streamlit_app.py
```

### **4. Acessar**
Abra no navegador: `http://localhost:8501`

---

## 📦 Estrutura do Projeto

```
meta-ads-scraper/
│
├── streamlit_app.py      # Código principal do app
├── requirements.txt      # Dependências Python
├── packages.txt          # Pacotes do sistema (Chrome)
├── README.md            # Este arquivo
└── .gitignore           # Arquivos ignorados pelo Git
```

## 🐛 Troubleshooting

### Chrome não encontrado
Adicione no `packages.txt`:
```
chromium
chromium-driver
```

### App muito lento
- Reduza número de scrolls
- Use cache do Streamlit
- Migre para servidor dedicado

### Erro 500
- Verifique se o Chrome está instalado
- Aguarde e tente novamente (API do Meta pode estar instável)

---

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar!

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/MinhaFeature`
3. Commit: `git commit -m 'Adiciona MinhaFeature'`
4. Push: `git push origin feature/MinhaFeature`
5. Abra um Pull Request

---

## 👨‍💻 Autor

Criado com ❤️ por NobodyDiv

---

## 📞 Suporte

Encontrou um bug? Tem uma sugestão?

- 🐛 [Reportar Bug](https://github.com/davy908/MetaResultScrapper/issues)
- 💡 [Sugerir Feature](https://github.com/davy908/MetaResultScrapper/issues)
- 📧 Email: davyps908@gmail.com

---

## ⭐ Se ajudou, dê uma estrela!

Se este projeto foi útil, considere dar uma ⭐ no GitHub!

---

## 🔮 Roadmap

Próximas features planejadas:

- [ ] Adicionar filtros avançados
- [ ] Exportar para CSV/Excel
- [ ] Dashboard com gráficos
- [ ] Histórico de buscas
- [ ] API REST
- [ ] Autenticação de usuários
- [ ] Agendamento de buscas automáticas

---

## 📚 Links Úteis

- [Documentação do Streamlit](https://docs.streamlit.io)
- [Biblioteca de Anúncios Meta](https://www.facebook.com/ads/library/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)

---

**Made with 🕷️ and lots of ☕**
