import urllib.request,re
UA={'User-Agent':'Mozilla/5.0 (compatible; RVBioenergia/1.0)'}
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','ignore')
    except Exception as e: return 'ERRO '+str(e)[:100]
def clean(t): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t))
for u in ['https://www.cepea.org.br/br/indicador/etanol.aspx','https://www.cepea.org.br/br/indicador/etanol-hidratado.aspx','https://www.cepea.org.br/br/indicador/etanol-anidro.aspx','https://cepea.org.br/br/indicador/etanol.aspx']:
    t=get(u); print('==',u,len(t),t[:60].replace('\n',' '))
    if not t.startswith('ERRO'):
        x=clean(t); i=x.find('Indicador'); 
        print(x[:100]); print([m for m in re.findall(r'\d{2}/\d{2}/\d{4}[^A-Za-z]{0,40}',x)][:14])
        print(sorted(set(re.findall(r'href="([^"]*indicador[^"]*)"',t)))[:30])
for u in ['https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/arq-sintese-semanal/2026/sintese-precos-45.pdf','https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/arq-sintese-semanal/2026/sintese-precos-46.pdf','https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/arq-sintese-semanal/2026/sintese-precos-47.pdf','https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos']:
    t=get(u); print('== ANP',u[-45:],len(t),t[:70].replace('\n',' '))
    for m in sorted(set(re.findall(r'href="([^"]*(?:sintese|semanal)[^"]*)"',t)))[:20]: print('  ',m)
