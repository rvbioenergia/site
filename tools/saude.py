"""Guardião do site RV Bioenergia: confere se os dados estão frescos e se o site está no ar.
Se algo estiver errado, abre (ou atualiza) uma Issue 'alerta-site' no GitHub — que chega por e-mail —
e fecha sozinha quando tudo volta ao normal. Roda todo dia útil depois do robô de dados."""
import json, os, re, sys, urllib.request
from datetime import datetime, timedelta

HOJE = (datetime.utcnow() - timedelta(hours=3)).date()          # data em Brasília
UA = {'User-Agent': 'Mozilla/5.0 (compatible; RVBioenergia-Saude/1.0)'}

def d_br(s):
    for f in ('%d/%m/%Y', '%d/%m/%y'):
        try: return datetime.strptime(s.strip(), f).date()
        except Exception: pass
    return None

def http(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode('utf-8', 'ignore')

problemas, avisos = [], []
d = json.load(open('dados-mercado.json', encoding='utf-8'))

# 1) o robô rodou hoje?
at = datetime.fromisoformat(d['atualizado']).date()
if at != HOJE and (HOJE - at).days >= 1 and HOJE.weekday() < 5:
    problemas.append(f"O robô de dados não atualizou hoje (última atualização: {at:%d/%m/%Y}).")

# 2) frescor de cada dado
def idade(s):
    dt = d_br(s or '')
    return (HOJE - dt).days if dt else None

i = idade(d.get('brent', {}).get('data'))
if i is None or i > 4: problemas.append(f"Brent desatualizado (data: {d.get('brent',{}).get('data')}).")
i = idade((d.get('pln_diario') or {}).get('data'))
if i is None or i > 6: problemas.append(f"PLN diário do CEPEA desatualizado (data: {(d.get('pln_diario') or {}).get('data')}).")
sf = (d.get('etanol_paulinia') or {}).get('semana_fim')
i = idade(sf)
if i is None or i > 9: problemas.append(f"Etanol semanal CEPEA desatualizado (semana até: {sf}).")
n = d.get('nacional', {})
if n.get('municipios_pesquisados', 0) < 20: problemas.append(f"Paridade com poucas capitais ({n.get('municipios_pesquisados')}/27).")
nots = d.get('noticias', [])
fontes = {x.get('fonte') for x in nots}
if len(nots) < 6 or len(fontes) < 3:
    problemas.append(f"Notícias fracas: {len(nots)} itens de {len(fontes)} fonte(s) (esperado: 6+ itens, 3+ fontes).")
if nots:
    mais_nova = min((idade(x.get('data')) for x in nots if idade(x.get('data')) is not None), default=None)
    if mais_nova is None or mais_nova > 5: problemas.append("Notícias sem nenhuma publicação nos últimos 5 dias.")

# 3) ANP: aviso (não derruba o site; só afeta a exclusão de capitais sem preço)
per = ((d.get('anp_ultima') or {}).get('periodo') or (d.get('diagnostico_anp') or {}).get('periodo') or '')
m = re.findall(r'\d{2}/\d{2}/\d{4}', per)
if not m: avisos.append("ANP: período da Síntese Semanal não identificado.")
else:
    i = idade(m[-1])
    if i is not None and i > 21: avisos.append(f"ANP: última Síntese Semanal lida é de {m[-1]} ({i} dias).")

# 4) site no ar e igual ao repositório
try:
    home = http('https://rvbioenergia.com.br/')
    if 'RV Bioenergia' not in home: problemas.append("A página https://rvbioenergia.com.br abriu, mas sem o conteúdo esperado.")
    live = json.loads(http('https://rvbioenergia.com.br/dados-mercado.json?c=' + str(int(datetime.utcnow().timestamp()))))
    if live.get('atualizado') != d.get('atualizado'):
        la = datetime.fromisoformat(live['atualizado'])
        if (datetime.fromisoformat(d['atualizado']) - la) > timedelta(hours=3):
            problemas.append(f"O site no ar está com dados mais antigos que o repositório (no ar: {la:%d/%m %H:%M}).")
except Exception as e:
    problemas.append(f"Não consegui abrir o site no ar: {str(e)[:100]}")

# ---------- Issue no GitHub ----------
repo, tok = os.environ.get('GITHUB_REPOSITORY'), os.environ.get('GITHUB_TOKEN')
def gh(method, path, body=None):
    req = urllib.request.Request('https://api.github.com/repos/' + repo + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization': 'Bearer ' + tok, 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'rv-saude'})
    with urllib.request.urlopen(req, timeout=30) as r:
        t = r.read().decode(); return json.loads(t) if t else {}

print('PROBLEMAS:', problemas); print('AVISOS:', avisos)
if not (repo and tok):
    sys.exit(1 if problemas else 0)

try: gh('POST', '/labels', {'name': 'alerta-site', 'color': 'd93f0b', 'description': 'Alerta automático de saúde do site'})
except Exception: pass
abertas = gh('GET', '/issues?state=open&labels=alerta-site&per_page=5')
if problemas or avisos:
    corpo = "## Alerta automático do site rvbioenergia.com.br\n\n"
    if problemas: corpo += "**Problemas**\n" + "\n".join('- ' + p for p in problemas) + "\n\n"
    if avisos: corpo += "**Avisos**\n" + "\n".join('- ' + a for a in avisos) + "\n\n"
    corpo += f"_Verificado em {datetime.utcnow()-timedelta(hours=3):%d/%m/%Y %H:%M} (Brasília). A manutenção do site é automática: o assistente (Claude) é acionado para corrigir. Esta nota fecha sozinha quando tudo normalizar._"
    titulo = "Alerta do site: " + ("; ".join(p.split(' (')[0].rstrip('.') for p in problemas)[:90] if problemas else "aviso de fonte")
    if abertas:
        if abertas[0]['body'] != corpo: gh('PATCH', f"/issues/{abertas[0]['number']}", {'body': corpo, 'title': titulo})
    else:
        gh('POST', '/issues', {'title': titulo, 'body': corpo, 'labels': ['alerta-site']})
else:
    for a in abertas:
        gh('POST', f"/issues/{a['number']}/comments", {'body': 'Tudo normalizado na verificação de hoje. Fechando.'})
        gh('PATCH', f"/issues/{a['number']}", {'state': 'closed'})
sys.exit(1 if problemas else 0)
