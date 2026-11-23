import urllib.request,re
UA={'User-Agent':'Mozilla/5.0 (compatible; RVBioenergia/1.0)'}
t=urllib.request.urlopen(urllib.request.Request('https://www.cepea.org.br/br/indicador/etanol.aspx',headers=UA),timeout=30).read().decode('utf-8','ignore')
x=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','|',t)); x=re.sub(r'\|(\s*\|)+','|',x)
i=x.find('19/11/2026'); print(x[i-700:i+1400]); print('-----'); j=x.find('19/11/2026',i+1500); print(x[j-500:j+700])
