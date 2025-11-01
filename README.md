# ⚡ Enel Billing Bot – Automação de Download de Contas de Energia

Este projeto é um **bot automatizado em Python** criado para **baixar e organizar automaticamente as faturas de energia elétrica** do portal da Enel Distribuição RJ.  
Ele acessa o site, realiza login com dados pré-configurados, solicita o envio de código via SMS, valida o código inserido pelo usuário e baixa o PDF da fatura, **renomeando-o automaticamente de forma organizada**.

---

## 🚀 Funcionalidades Principais

✅ Interface simples para escolher a unidade consumidora  
✅ Automação completa via Selenium e PyAutoGUI  
✅ Preenchimento automático de formulário  
✅ Interação semiautomática com verificação SMS  
✅ Download automático do PDF da conta  
✅ Renomeia o arquivo conforme referência e mês da fatura  
✅ Armazena os PDFs organizados em uma pasta específica  

---

## 🧰 Tecnologias Utilizadas

- **Python 3.13+**
- **Selenium** + **undetected_chromedriver**
- **PyAutoGUI**
- **Tkinter**
- **Pathlib**, **time**, **shutil**

---

## 🖥️ Como Executar o Projeto

### 1️⃣ Instale as dependências
No terminal, execute:

pip install selenium undetected-chromedriver pyautogui
### 2️⃣ Estrutura de pastas esperada
mathematica
Copiar código
Documents/
 ├── Usina/
 │   ├── Contas/  ← PDF das contas baixadas
 │   └── Unidade Consumidora Usina.txt  ← Lista de unidades consumidoras
 └── Enel.py  ← Script principal

### 3️⃣ Formato do arquivo de unidades
O arquivo Unidade Consumidora Usina.txt deve seguir o formato:
yaml
Copiar código
nome da unidade consumidora 1: codigo da unidade consumidora 1
nome da unidade consumidora 2: codigo da unidade consumidora 2
nome da unidade consumidora 3: codigo da unidade consumidora 3
...

### 4️⃣ Executar o script
No terminal:
bash
Copiar código
python Enel.py
O programa abrirá uma janela pedindo que você escolha a unidade e depois iniciará o processo de automação.

🧠 Lógica do Processo
1️⃣ O usuário escolhe a unidade consumidora via interface Tkinter
2️⃣ O script abre o navegador em modo stealth (não detectável como bot)
3️⃣ Preenche os campos de número e CNPJ
4️⃣ Aguarda o captcha (que o usuário clica manualmente)
5️⃣ Solicita e valida o código SMS
6️⃣ Clica em “2ª via” da conta mais recente e faz o download do PDF
7️⃣ Renomeia o arquivo com base no nome da unidade e referência (ex: casa_XPTO_ref.mesano.pdf)

📂 Organização e Salvamento
Os arquivos são salvos automaticamente na pasta:

makefile
Copiar código
C:\Users\<usuário>\Documents\Usina\Contas
E são renomeados conforme o padrão:

php-template
Copiar código
<unidade>_ref.<mês><ano>.pdf
Exemplo:
rust
Copiar código
praia_de_icaraí_ref.junho2025.pdf

💡 Melhorias Futuras
Integração completa via Selenium (remover dependência do PyAutoGUI)
Solução automática de Captcha com reconhecimento de imagem
Interface gráfica completa (Tkinter GUI)
Geração automática de relatório mensal

👨‍💻 Autor
Rafael Coelho Recker
📍 Brasil
💼 Projeto pessoal de automação para otimização de processos administrativos

🌐 LinkedIn: https://www.linkedin.com/in/rafael-coelho-recker-/
