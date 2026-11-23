import urllib.request,re,sys
sys.path.insert(0,'.')
import coletor
UA={'User-Agent':'Mozilla/5.0 (compatible; RVBioenergia/1.0)'}
feeds=['https://www.noticiasagricolas.com.br/rss/etanol.rss','https://www.novacana.com/feed','https://www.udop.com.br/rss.php',
'https://eixos.com.br/feed/','https://brasilenergia.com.br/feed','https://www.petronoticias.com.br/feed','https://www.canalrural.com.br/feed/',
'https://globorural.globo.com/rss/ultimas/feed.xml','https://www.biodieselbr.com/rss.xml','https://agenciabrasil.ebc.com.br/rss/economia/feed.xml',
'https://jornalcana.com.br/feed/','https://www.gov.br/anp/pt-br/RSS','https://agenciainfra.com/blog/feed/','https://www.udop.com.br/noticias/rss','https://mercadoeconsumo.com.br/feed/','https://www.cnnbrasil.com.br/economia/feed/','https://valor.globo.com/rss/','https://www.agrolink.com.br/rss/noticias','https://revistaopetroleo.com.br/feed/','https://www.biodieselbr.com/feed']
for u in feeds:
    try:
        c=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=15).read().decode('utf-8','ignore')
    except Exception as e:
        print('X',u,str(e)[:50]); continue
    tt=re.findall(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>',c)[1:15]
    rel=[t for t in tt if coletor._relevante(t.strip())]
    print('OK',u,len(c),'itens',len(tt),'relevantes',len(rel),'|',(rel[0][:70] if rel else (tt[0][:60] if tt else '')))
