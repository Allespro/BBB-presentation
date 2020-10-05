 #https://vks.mtuci.ru/bigbluebutton/presentation/ab6cc0297149c9405a484f5f9ffbaa832aba4b6a-1601532974113/ab6cc0297149c9405a484f5f9ffbaa832aba4b6a-1601532974113/1ba6008a86a183412f417e1529b5a222d98cf53c-1601533016025/svg/
import cherrypy, requests, random, os, cairosvg, img2pdf
from cherrypy import tools
from PIL import Image

def sorter(filename) -> int:
	return int(filename.split('/')[2].split('.')[0])

def download(link, number, folder) -> bool:
	f = requests.get(link+"/"+str(number))
	if f.status_code == 200:
		open(os.path.join(folder, str(number)+".svg"), "wb").write(f.content)
		cairosvg.svg2png(url=os.path.join(folder, str(number)+".svg"), write_to=os.path.join(folder, str(number)+".png"))
		Image.open(os.path.join(folder, str(number)+".png")).convert('RGB').save(os.path.join(folder, str(number)+".jpg"))
		return True
	else:
		return False

def compile(folder):
	filelist = []
	print(os.listdir(folder))
	for file in os.listdir(folder):
		if file.endswith(".jpg"):
			filelist.append(os.path.join(folder, file))
	filelist = sorted(filelist, key = sorter)
	print (filelist)
	with open(os.path.join(folder, "ready.pdf"),"wb") as pdf:
		pdf.write(img2pdf.convert(filelist))
	for file in os.listdir(folder):
		if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".svg"):
			os.remove(os.path.join(folder, file))

def create_random_folder(m) -> str:
	small_letters = "abcdefghjkmnpqrstuvwxyz"
	big_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
	digits = "23456789"
	symbols = small_letters + big_letters + digits
	folder = random.choice(small_letters) + random.choice(big_letters) + random.choice(digits)
	while len(folder) < m:
		folder += random.choice(symbols)
	if not os.path.exists(os.path.join('assets',folder)):
		os.makedirs(os.path.join('assets',folder))
		return os.path.join('assets',folder)






config = {
	'global' : {
		'server.socket_host' : '0.0.0.0',
		'server.socket_port' : int(os.environ.get('PORT', 5000)),
		'server.thread_pool' : 8,
		'server.max_request_body_size' : 0,
		'server.socket_timeout' : 60,
		'tools.staticdir.root' : os.path.abspath('assets'),
		'tools.staticdir.on' : True,
		'tools.staticdir.dir' : '',
		'response.stream': True
  }
}

class Root(object):
	@cherrypy.expose
	def index(self):
		return """ <!DOCTYPE html>
<html>
   <head><link rel="stylesheet" href="style.css" type="text/css"></head>
   <body>
   <div class="Corner-block">Разработчик сиего ужоса <a href="https://vk.com/setup.json">setup.json</a></div>
   <div class="Wrapper">
  <h1 class="Title">Спаси и сохрани</h1>
  <div class="Input">
  <form action = "downloader" method = "post">
    <input name="link" type="text" id="input" class="Input-text" placeholder="Ссылка на слайд презентации">
    <input type="submit" class="Input-button" value="Начать загрузку">
    </form>
  </div>
  </div>
   </body>
</html>
"""
   
	@cherrypy.expose
	def downloader(self, link):
		yield """<!DOCTYPE html>
<html>
   <head><link rel="stylesheet" href="style.css" type="text/css"></head>
   <body>
   <div class="Corner-block">Разработчик сиего ужоса <a href="https://vk.com/setup.json">setup.json</a></div>
   <div class="Wrapper">
  <h1 class="Title">Спаси и сохрани</h1>
  <div class="Input">"""
		folder = create_random_folder(8)
		link = link[::-1].split('/', 1)[1][::-1]
		download_number = 1
		yield "<p class=\"Log-text\">Скачан слайд "
		while download(link, download_number, folder):
			yield str(download_number)+" "
			download_number += 1
		yield "</p>"
		compile(folder)
		yield """<p class="Log-text"> <a href="""+os.path.join(folder.split("/")[1], "ready.pdf")+"""> Открыть презентацию</a></p>
		<p class="Log-text"> <a href="""+os.path.join(folder.split("/")[1], "ready.pdf")+""" download> Скачать презентацию</a></p>
		<p class="Log-text">(ссылка активна 15 минут)</p>
   		</div>
   </body>
</html>"""
		os.system("sleep 900 && rm -r ./"+folder+" &")

if __name__ == '__main__':
	cherrypy.quickstart(Root(), '/', config=config)