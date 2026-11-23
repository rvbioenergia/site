import urllib.request,re,sys
UA={'User-Agent':'Mozilla/5.0 (compatible; RVBioenergia/1.0)'}
def get(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','ignore')
    except Exception as e: return 'ERRO '+str(e)[:100]
for n,u in [('hid','https://www.noticiasagricolas.com.br/cotacoes/sucroenergetico/indicador-semanal-etanol-hidratado-cepea-esalq'),('ani','https://www.noticiasagricolas.com.br/cotacoes/sucroenergetico/indicador-semanal-etanol-anidro-cepea-esalq')]:
    t=get(u); print('==',n,len(t)); 
    txt=re.sub(r'<[^>]+>',' ',t); txt=re.sub(r'\s+',' ',txt)
    i=txt.find('Data'); print(txt[i:i+500] if i>=0 else txt[:300])
t=get('https://www.cepea.org.br/br/indicador/etanol-diario-paulinia.aspx'); print('== PLN',len(t))
txt=re.sub(r'<[^>]+>',' ',t); txt=re.sub(r'\s+',' ',txt)
for m in re.finditer(r'\d{2}/\d{2}/\d{4}\s+[\d.,]+',txt): print(m.group(0))
for u in ['https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/arq-sintese-semanal/2026/sintese-precos-46.pdf',
          'https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/sintese-semanal-do-comportamento-dos-precos-dos-combustiveis',
          'https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/sintese-semanal-do-comportamento-dos-precos-dos-combustiveis']:
    t=get(u); print('== ANP',u[-60:],len(t),t[:80].replace('\n',' '))
    for m in sorted(set(re.findall(r'href="([^"]*sintese[^"]*)"',t)))[:25]: print('  ',m)
