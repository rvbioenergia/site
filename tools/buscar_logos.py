import os, re, json, urllib.parse, requests, urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings()
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36','Accept-Language':'pt-BR,pt;q=0.9','Accept':'text/html,application/xhtml+xml,*/*'}
ALVOS={'usina-bom-jesus':['usinabomjesus.com.br','usinabomjesus.com.br'],'cooperativa-pindorama':['cooperativapindorama.com.br'],'usina-taquari':['usinataquari.com.br','taquari.com.br'],'usina-trapiche':['usinatrapiche.ind.br','usinatrapiche.com.br']}
OUT='candidatos6'; os.makedirs(OUT,exist_ok=True); log={}
for nome,doms in ALVOS.items():
    d=f'{OUT}/{nome}'; os.makedirs(d,exist_ok=True); n=0; log[nome]=[]
    for dom in doms:
        for host in (dom,'www.'+dom):
            for sch in ('https://','http://'):
                u=sch+host
                try:
                    r=requests.get(u,headers=UA,timeout=20,verify=False,allow_redirects=True)
                    log[nome].append(f'{u} {r.status_code} {len(r.text)}'); print(nome,u,r.status_code,len(r.text),flush=True)
                    if r.status_code!=200: continue
                    soup=BeautifulSoup(r.text,'html.parser'); cs=[]
                    def add(x):
                        if x and not x.startswith('data:'): cs.append(urllib.parse.urljoin(r.url,x.strip()))
                    for img in soup.find_all('img'):
                        blob=' '.join([img.get('src') or '',img.get('alt') or '',' '.join(img.get('class',[])),img.get('data-src') or '']).lower()
                        if 'logo' in blob or 'marca' in blob: add(img.get('src') or img.get('data-src'))
                    for m in soup.find_all('meta'):
                        if m.get('property') in ('og:image',): add(m.get('content'))
                    for l in soup.find_all('link',rel=True):
                        if 'icon' in ' '.join(l['rel']).lower(): add(l.get('href'))
                    for m in re.finditer(r'["\'(=\s]([^"\'()\s<>]*(?:logo|marca)[^"\'()\s<>]*\.(?:png|svg|webp|jpg|jpeg))',r.text,re.I): add(m.group(1).replace('\\/','/'))
                    seen=set()
                    for c in cs:
                        if c in seen or n>=14: continue
                        seen.add(c)
                        try:
                            ir=requests.get(c,headers=UA,timeout=20,verify=False)
                            ct=ir.headers.get('content-type','').split(';')[0]
                            ext={'image/png':'png','image/jpeg':'jpg','image/svg+xml':'svg','image/webp':'webp','image/gif':'gif'}.get(ct)
                            if ir.status_code==200 and ext and 300<len(ir.content)<3_000_000:
                                open(f'{d}/{n:02d}.{ext}','wb').write(ir.content); log[nome].append(f'  img {n:02d}.{ext} {c}'); n+=1
                        except Exception as e: pass
                    if n: break
                except Exception as e:
                    log[nome].append(f'{u} ERRO {str(e)[:70]}'); print(nome,u,'ERRO',str(e)[:70],flush=True)
            if n: break
        if n: break
json.dump(log,open(OUT+'/log.json','w'),ensure_ascii=False,indent=1)
