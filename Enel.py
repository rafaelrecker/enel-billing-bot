import json
import time
import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as sd
import pyautogui
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import glob, shutil
from pathlib import Path

# ========================== CONFIG. (edite somente aqui) ==========================
# Deixe CNPJ = "" em repositório público. Localmente você pode preencher para não pedir toda vez.
CNPJ = ""  # ex.: "12345678000199" (somente números). VAZIO => o app perguntará em tempo de execução.

# Arquivo com as unidades consumidoras (formato: "apelido: numero" por linha).
UNIDADES_PATH = Path(__file__).with_name("unidades.txt")  # ou Path("caminho/para/Unidade Consumidora Usina.txt")

# Pastas usadas no fluxo de download/renomeio:
CHROME_DOWNLOAD_DIR = Path.home() / "Downloads"           # onde o Chrome salva
DOWNLOADS_MONITOR_DIR = Path.home() / "Downloads"         # onde monitoramos a chegada do PDF
DESTINO_DIR = Path.home() / "Downloads" / "Enel_Contas"   # destino final

# ================================================================================
def ler_dados_unidades(path_txt: str) -> dict:
    dados = {}
    with open(path_txt, "r", encoding="utf-8") as f:
        for linha in f:
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                dados[chave.strip().lower()] = valor.strip()
    return dados

def selecionar_unidade(dados_unidades: dict) -> str:
    root = tk.Tk()
    root.title("Selecione a Unidade")
    root.geometry("400x150")
    root.resizable(False, False)
    root.attributes('-topmost', True)
    root.lift()

    escolha = tk.StringVar(master=root)
    ttk.Label(root, text="Selecione a unidade desejada:", font=("Arial", 12)).pack(pady=10)
    combo = ttk.Combobox(
        root,
        textvariable=escolha,
        values=list(dados_unidades.keys()),
        state="readonly",
        width=40
    )
    combo.current(0)
    combo.pack(pady=5)
    ttk.Button(root, text="Confirmar", command=root.quit).pack(pady=10)

    root.mainloop()
    root.destroy()
    return escolha.get().strip().lower()

if __name__ == "__main__":
    # 1) Ler e escolher unidade
    file_path = str(UNIDADES_PATH)
    dados_unidades = ler_dados_unidades(file_path)
    unidade_chave = selecionar_unidade(dados_unidades)
    numero_unidade = dados_unidades[unidade_chave]
    print(f"Unidade escolhida: {unidade_chave} → {numero_unidade}")

    # 2–5) Abre o Chrome em modo stealth e já configura o download automático
    opts = uc.ChromeOptions()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--incognito")
    opts.add_argument("--start-maximized")
    prefs = {
        "download.default_directory": str(CHROME_DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    opts.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=opts, headless=False, version_main=141)
    driver.maximize_window()

    # página da Enel
    driver.get("https://www.eneldistribuicao.com.br/rj/AcessoRapidosegundavia.aspx")
    time.sleep(5)

    # 6) Rolar para expor campos
    pyautogui.scroll(-650)
    time.sleep(1)

    # 7) Digitar unidade
    pyautogui.moveTo(465, 358); pyautogui.click(); time.sleep(1)
    pyautogui.write(numero_unidade)

    # 8) Digitar CNPJ (usa o da CONFIG; se vazio, pergunta)
    cnpj = CNPJ
    if not cnpj:
        root = tk.Tk(); root.withdraw()
        cnpj = sd.askstring("CNPJ", "Digite o CNPJ da empresa (somente números):")
        if not cnpj:
            print("❌ Nenhum CNPJ informado – encerrando.")
            driver.quit()
            raise SystemExit(1)

    pyautogui.moveTo(465, 480); pyautogui.click(); time.sleep(1)
    pyautogui.write(cnpj)

    # 9) Captcha (manual)
    pyautogui.moveTo(479, 563); pyautogui.click(); time.sleep(2)

    # 10) Próximo
    pyautogui.moveTo(785, 694); pyautogui.click(); time.sleep(5)

    # 11) Enviar SMS
    pyautogui.moveTo(700, 419); pyautogui.click(); pyautogui.press("enter")

    # 12) Continuar
    time.sleep(5)
    pyautogui.moveTo(668, 594); pyautogui.click()

    # 13) Focar no campo do SMS
    time.sleep(2)
    pyautogui.moveTo(123, 465); pyautogui.click()

    # 14) Caixa de diálogo para inserir SMS
    root = tk.Tk(); root.withdraw()
    codigo_sms = sd.askstring("Código SMS", "Digite o código recebido por SMS:")

    # 15) Escrever e enviar SMS
    if codigo_sms:
        pyautogui.write(codigo_sms); pyautogui.press("enter")
    else:
        print("❌ Nenhum código inserido – encerrando.")
        driver.quit()
        raise SystemExit(1)

    # 16) Esperar carregar contas
    time.sleep(15)

    # 17–18) Selecionar “2ª via” usando Selenium (copy selector)
    check_css = "#CONTENT_segviarapida_GridViewSegVia_CheckFatura_0"
    elem = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, check_css))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
    time.sleep(0.5)
    try:
        elem.click()
    except Exception:
        driver.execute_script("arguments[0].click();", elem)
    time.sleep(1)

    # 19) Ler referência da tabela antes do download
    ref_el = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,
            "#CONTENT_segviarapida_GridViewSegVia > tbody > tr:nth-child(2) > td:nth-child(3)"
        ))
    )
    ref_text = ref_el.text  # ex: "07/2025"
    mês_num, ano = ref_text.split("/")
    meses_map = {
        "01":"janeiro","02":"fevereiro","03":"março","04":"abril",
        "05":"maio","06":"junho","07":"julho","08":"agosto",
        "09":"setembro","10":"outubro","11":"novembro","12":"dezembro"
    }
    mes_nome = meses_map[mês_num.zfill(2)]
    novo_nome = f"{unidade_chave}_ref.{mes_nome}{ano}.pdf"
    print("Renomeando para:", novo_nome)

    # 20) Preparar lista de downloads antes do click
    downloads = DOWNLOADS_MONITOR_DIR
    before = set(downloads.glob("*.pdf"))

    # 21) Clicar em “Salvar PDF” via Selenium (copy selector)
    salvar_css = "#CONTENT_segviarapida_btnSalvarPDF"
    btn_pdf = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, salvar_css))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_pdf)
    time.sleep(0.5)
    try:
        btn_pdf.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn_pdf)
    time.sleep(15)

    # 22) Confirmar Save-As pressionando Enter
    pyautogui.press("enter")

    # 23) Aguardar até o novo PDF aparecer em Downloads (até 30s)
    deadline = time.time() + 30
    while time.time() < deadline:
        after = set(downloads.glob("*.pdf"))
        novos = {p for p in (after - before) if not p.name.endswith(".crdownload")}
        if novos:
            pdf_file = novos.pop()
            break
        time.sleep(0.5)
    else:
        raise TimeoutError("PDF não apareceu em Downloads dentro de 30s")

    # 24) Mover e renomear para pasta destino (parametrizada)
    destino_dir = DESTINO_DIR
    destino_dir.mkdir(parents=True, exist_ok=True)
    target = destino_dir / novo_nome

    # se já existir, apaga antes
    if target.exists():
        target.unlink()

    shutil.move(str(pdf_file), str(target))
    print("✅ PDF movido e renomeado para:", target)
