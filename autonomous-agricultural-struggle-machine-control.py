from tkinter import *
from time import sleep


##########################################################################################
##### STATİK DEĞİŞKENLER. PROGRAM SÜRESİNCE DEĞİŞMESİ BEKLENMEYEN ÖNCEDEN TANIMLADIĞIMIZ BİR CONFIG
##########################################################################################
FIELD_WIDTH = 800
FIELD_HEIGHT = 600
SPEED = 10                      # artarsa araba daha yavaş hareket eder
BLOCK_SIZE = 40                 # her bir karenin boyunu tutar. Daha büyük sayı = daha büyük kareler                         
VEHICLE_SIZE = 2                # aracımızın kare cinsinden uzunluğu
STORAGE = 4                     # aracın ilaç deposunun büyüklüğü
VEHICLE_COLOR = '#FF0000'       # araç rengi
TREE_COLOR = '#00FF00'          # ağaçların ilaçlanmadan önceki rengi
BASE_COLOR = '#FFA500'
VISITED_TREE_COLOR = '#88FF88'  # ilaçlanan ağacın rengi
BACKGROUND_COLOR = '#115153'    # arkaplan rengi
##########################################################################################


##########################################################################################
##### CLASS TANIMLAMALARI ################################################################
##########################################################################################
class Vehicle:
    def __init__(self):                                 # Yaratıcı fonksyion, argümana ihtiyacı yok
        self.coordinates = []                           # Aracın koordinat listesi, her bir eleman aracın bir parçasının konumunu temsil edecek
        self.squares = []                               # Ağaçtaki gibi her koordinata yönelik square objeleri
        self.storage = STORAGE                          # Her araca taşıyabileceği bir maksimum ilaç miktarı verdik. Default olarak 4.
        self.checkpoint = [BLOCK_SIZE, BLOCK_SIZE]      # Boşaltım sonrası devam edilecek ağacın id'si
        self.queue = Tree                               # Aracın sorumlu olduğu ağaç listesi

        for i in range(0, VEHICLE_SIZE):        # Aracın parçalarını ilk olarak burda koordinatlarla yaratıyoruz. 
            self.coordinates.append([0, 0])     # Aslında arbanın her parçası 0,0 koordinatında üst üste başlıyor

        for x, y in self.coordinates:           # Aracın koordinatlarına yönelik square objeleri oluşacak (kırmızı kareler  )
            square = canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=VEHICLE_COLOR, tag='vehicle')   # koordinatlar için kareler yarat
            self.squares.append(square)         # Yaratılan kareyi squares listesine ekle

    def supply(self):                                   # Aracın ilaçlama methodu, parametre olarak bir Tree nesnesi bekler        
        global supplyCount

        sleep(0.3)                                            # İlaçlama varmış gibi sistemi 0.3 saniye uyut

        for tree in self.queue:                               # Aracın sahip olduğu ağaç listesindeki her bir ağaç için
            if tree.coordinates == self.coordinates[0]:       # Eğer araç bir ağaca denk gelmişse
                tree.visited = True                           # İlaçlanan ağacı ziyaret edilmiş olarak değiştir
                tree.color = VISITED_TREE_COLOR               # İlaçlanan ağacın rengini değiştir

                self.storage -= 1                             # Aracın ilaç haznesinden bir eksilt
                supplyCount += 1                              # Total ilaçlanan ağaç miktarını arttır
                
                canvas.itemconfig(tree.square, fill=tree.color)                             # Canvas nesnesi üzerinden ilaçlanacak ağaca ulaşıp rengini değiştirir
                label.config(text="Supplied: {}/{}".format(supplyCount, len(self.queue)))   # Üstteki dinamik sayım textini güncelle. 
                break                                         # break, for döngüsünü bitirir. ilaçlama yapılınca burada işimiz bitiyor.

        for tree in trees:                                    # sıradaki ağacın koordinatlarını kaydeder
            if not tree.visited:
                self.checkpoint = tree.coordinates            # sırayla ağaçlara bakar ve ziyaret edilmeyen bulunca kaydedip döngüden çıkar.
                break

        if self.storage == 0:                                 # ilaçlamadan sonra depo boş mu diye kontrol et
            self.checkpoint = [0, 0]                          # hedefi (0, 0) koordinatları yani base yap.

    def refill(self):                                         # ilaç deposunu doldurma methodu
        self.storage = STORAGE                                # Başta tanımlanan STORAGE değeri kadar depoyu doldur

        for tree in self.queue:                               # Listede ziyaret edilmemiş ağaçlara bakarak sıradaki hedefi belirler
            if not tree.visited:
                self.checkpoint = tree.coordinates
                break        

    def predict_next(self):                            # sıradaki hareketin ne yönde olacağını bulan method.     
        x, y = self.coordinates[0]                     # aracın önünün koordinatını kopyala

        if y < self.checkpoint[1]:                     # aracın hedefe yönelik konumuna göre y düzeyinde yönünü belirler.
            y += BLOCK_SIZE                            
            return x, y                                # tek seferde x veya y yi buluyoruz. Aksi takdirde çapraz giderdi.
        elif y > self.checkpoint[1]:
            y -= BLOCK_SIZE
            return x, y
        
        if x + BLOCK_SIZE <= self.checkpoint[0]:       # bu if bloğu sadece araç ve hedef aynı y düzeyinde ise çalışır.
            x += BLOCK_SIZE                            # Araç daha sağdaysa sola, soldaysa sağa gitmesini söyler
        else:
            x -= BLOCK_SIZE                            
        
        return x, y


class Tree:
    def __init__(self, id, coordinates, square):    # Tree nesnesini yaratan fonksiyon. Koordinat ve square objesine ihtiyacı var
        self.id = id                                # Her bir ağaca ayrı ayrı referans yapabilmek için id verdik.
        self.coordinates = coordinates              # Ağaç için coordinates adlı bir nitelik yarat, değerini alınan argümana eşitle
        self.square = square                        # Ağaç için square adlı bir nitelik yarat, değerini alınan argümana eşitle
        self.visited = False                        # Ağaç için ilaçlanıp ilaçlanmadığını niteleyen, sadece Doğru veya Yanlış olabilecek bir nitelik yarat, default olarak tüm ağaçlar ilk olarak False yaptık
        self.color = TREE_COLOR                     # Ağaç için default renk verdik. İlaçlanmayan ağaçlar bu renktedir.
##########################################################################################

##########################################################################################
##### METHOD/FONKSIYON TANIMLAMALARI #####################################################
##########################################################################################
def advance(vehicle, trees):                  # Programı diğer ana geçirir          
    x, y = vehicle.predict_next()             # (x, y), yani aracın bir sonraki adımda geleceği koordinatları hesapla

    square = canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill=VEHICLE_COLOR, tag='vehicle')   # yeni x ve y ye göre aracın ucunun geleceği kareyi çiz/yarat

    # insert ile herhangi bir indexe eklerken, append sadece en sona ekler
    vehicle.coordinates.insert(0, [x, y])           # aracın koordinatlarının başına yeni (x, y) ekle. Bu listenin 0 indexindeki yani ilk elemanı her zaman aracın başıdır.
    vehicle.squares.insert(0, square)               # aracın koordinatlarına göre yaratılan square objesini aracın listesine ekle. 

    canvas.delete(vehicle.squares[-1])              # yeni kare eklendiğine göre, aracın son parçasını silmeliyiz. [-1] indexi, sondan birinci elemanı gösterir
    del vehicle.squares[-1]                         # yukarıda görsel arayüzde resmi sildiğimiz gibi, şimdi aracın niteliklerindeki listelerden sondaki eski parçayı siliyoruz 
    del vehicle.coordinates[-1]                     # yukarı ile aynı, coordinates niteliği için
    
    for tree in trees:                                      # Aracın bulunduğu koordinatta ilaçlanmamış bir ağaç var mı diye kontrol eder.
        if vehicle.coordinates[0] == tree.coordinates:
            if not tree.visited:
                vehicle.supply()                            # Bulunduysa ilaçlama yapılır ve döngüden çıkılır
                break

    if [x, y] == [0, 0]:                                    # Eğer başlangıç noktasına gelindiyse depo dolumu yapılır
        vehicle.refill()

    window.after(SPEED, advance, vehicle, trees)       # ilk argüman: (ms cinsinden zaman) kadar süre geçtikten sonra, ikinci argüman: bu fonksiyonu çağır, diğer argümanlar bu fonksiyonun argümanları olacak


def populate_field():
    temp_id = 0                                                 # Sıradaki ağaca vermelik geçici id. 0 olarak başlayıp her ağaç için artacak

    trees = []                                                  # yaratılan ağaçları koyacağımız bir boş liste yarat
    for j in range(BLOCK_SIZE, FIELD_HEIGHT, 2*BLOCK_SIZE):      # BLOCK_SIZE den başlayıp FIELD_WITH'e kadar 4*BLOCK_SIZE adımlarla atla
        for i in range(BLOCK_SIZE, FIELD_WIDTH, 3*BLOCK_SIZE):   # 0 dan başlayıp FIELD_HEIGHT'e kadar 3*BLOCK_SIZE adımlarla atla

            square = canvas.create_oval(i, j, i + BLOCK_SIZE, j + BLOCK_SIZE, fill=TREE_COLOR)  # sol üst noktası (i, j) sağ alt noktası (i + BLOCK_SIZE, j + BLOCK_SIZE) olan oval çiz
            text = canvas.create_text(i, j, text=temp_id, fill='white')

            tree = Tree(temp_id, [i, j], square)         # yeni bir ağaç yaratır. ağaç yaratmak için sol üst nokta koordinatı ve çizilen obje lazım
            trees.append(tree)                           # oluşturulan ağacı en son döndürülecek listeye atar
            temp_id += 1

    canvas.create_rectangle(0, 0, 2*BLOCK_SIZE, BLOCK_SIZE, fill=BASE_COLOR)

    return trees
##########################################################################################

##########################################################################################
##### GORSEL ARAYÜZ İÇİN PENCERE YARATMA #################################################
##########################################################################################

window = Tk()                                       # görsel arayüz oluşturmamızı sağlayan kütüphaneyi kullanmak için ona window adını verdik
window.title('Harvest Simulator')                   # pencerenin başlığı
window.resizable(False, False)                      # window nesnesinin, pencerenin büyütülüp büyütülmeyeceğini belirleyen niteliği. ilk argüman x-axis için; ikinci y-axis için

# pencere elemanlarını yarat
label = Label(window, text="Supplied: 0/0", font=('ariel', 32))         # label adında bir Label yarattık, labellar yazıdır, ilk argüman üzerinde yaratılmasını istediğimiz pencere objesi, ikinci argüman yazısı, üçüncü argüman font
label.pack()                                                                        # labelin pack methodunu çağırdığında pencereye ekler

canvas = Canvas(window, bg=BACKGROUND_COLOR, height=FIELD_HEIGHT, width=FIELD_WIDTH) # canvas üzerinde çizim yapmamızı sağlar, ilk argüman ekleneceği pencere, ikinci: arkaplan rengi, üçüncü: yüksekliği, dördncü: genişliği
canvas.pack()                                                                       # canvası pencereye ekler

window.update()                                                                     # window'a kendini update edip görsel değişikliği yansıtması söylenir. Manuel güncelleme nedenimiz performans amaçlı
##########################################################################################

##########################################################################################
##### ANA AKIŞ ###########################################################################
##########################################################################################
vehicle = Vehicle()                 # yeni bir araç nesnesi yarat
trees = populate_field()            # Arazi için ağaçlar dik, ve koordinat listesini döndür

vehicle.queue = trees               # ağaç listesini aracın bir niteliği olarak ekliyoruz. araç üzerinden erişebilmek için
supplyCount = 0                     # total ilaçlanmış ağaç sayısı. 0 olarak başlıyor.

advance(vehicle, trees)             # Artık elimizde bir ağaç listesi ve araç var. Advance methoduna bunları vererek bir sonraki ana geçiyoruz.

window.mainloop()
##########################################################################################