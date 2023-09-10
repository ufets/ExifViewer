import exif
import tkinter as tk
from tkinter import filedialog as fd
import tkinter.messagebox as mb
import webbrowser
import qrcode
from PIL import Image, ImageTk
from tkinter import Label
import dict

def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        ww = self.winfo_screenwidth() // 2
        hh = self.winfo_screenheight() // 2
        w = self.winfo_screenwidth() // 4
        h = self.winfo_screenheight() // 4

        self.geometry('{}x{}+{}+{}'.format(ww, hh, w, h))
        self.wm_title('EXIF VIEWER')
        #self.iconbitmap("iconka.ico")
        self.config(bg="#383838")

        logo = ImageTk.PhotoImage(Image.open('logo.png'))
        self.img_label = Label(self, image=logo, bg='#383838')
        self.img_label.image = logo
        self.img_label.place(relx=.25, rely=.45, anchor="c")

        self.greeting = tk.Label(self, text='Добро пожаловать в\n Exif Viewer',
                                 bg='#383838', fg='#D1D1D1', font=('Arial', 28), justify='center')
        self.greeting.place(relx=.7, rely=.25, anchor="c", relwidth=0.5, relheight=0.25, bordermode='outside')

        self.btn_file = tk.Button(self, text="Выбрать фото и\nпоказать метаданные", bg='#454545', fg='#D1D1D1',
                                  font=('Arial', 12), relief="ridge", command=lambda: MainMenu.make_it_beautiful(self))
        self.btn_file.place(relx=.7, rely=.63, anchor="c", relwidth=0.25, relheight=0.125, bordermode='outside')

        self.warning = tk.Label(self, text='*Загружаемый файл должен иметь расширение .jpg', bg='#383838', fg='#FA9C9C',
                                font=('Arial', 10), justify='center')
        self.warning.place(relx=.7, rely=.8, anchor="c", relwidth=0.5, relheight=0.2, bordermode='outside')

    def get_exif(self):

        filename = fd.askopenfilename(title="Открыть файл", initialdir="/", filetypes=((".jpg", "*.jpg"),))

        if filename != '':
            if filename.endswith(".jpg"):
                with open("{}".format(filename), "rb") as ph:
                    self.photo = exif.Image(ph)

                if self.photo.has_exif and len(self.photo.get_all()) != 0:
                    tags = list(self.photo.list_all())
                    data_tags = []

                    for i in range(len(tags)):
                        data_tags.append(self.photo.get(tags[i]))

                    return tags, data_tags, filename

                else:
                    msg = u'    Метаданные уже очищены\n    Попробуйте другое фото'
                    mb.showinfo("Инфо", msg)
                    return None, None, None
            else:
                msg = u'    Неккоректный тип файла\n    Попробуйте еще раз'
                mb.showwarning("Предупреждение", msg)
                return None, None, None
        else:
            return None, None, None

    @staticmethod
    def save_to_file(tags, data_tags):
        file = fd.asksaveasfile(title="Сохранить файл", defaultextension=".txt", filetypes=((".txt", "*.txt"),))

        if file:
            for i in range(len(data_tags)):
                #file.write("{} : {}\n-----------------\n".format(tags[i], str(data_tags[i])))
                text = \
                    dict.translator(tags[i]) + '<' + tags[i] + '>' + '\n' + str(data_tags[i]) + '\n' + \
                    '_' * len(str(tags[i])) + '\n'
                file.write(text)

            file.close()

    @staticmethod
    def get_link(tags, data_tags):
        i = 0
        latituderef = ""
        link = "https://www.google.ru/maps/place/"

        for item in tags:
            if item == "gps_latitude":
                if data_tags[i][0] == 0:
                    return None

                link += str(int(data_tags[i][0])) + '°' + str(int(data_tags[i][1])) + '\'' + str(data_tags[i][2])
            if (item == "gps_latitude_ref") and (data_tags[i] != ''):
                latituderef = data_tags[i][0]
            i = i + 1

        if len(link) > len("https://www.google.ru/maps/place/"):
            link += "\'\'" + latituderef + '+'
            i = 0
            longtuderef = ""

            for item in tags:
                if item == "gps_longitude":
                    link += str(int(data_tags[i][0])) + '°' + str(int(data_tags[i][1])) + '\'' + str(data_tags[i][2])

                if (item == "gps_longitude_ref") and (data_tags[i] != ''):
                    longtuderef = data_tags[i][0]
                i = i + 1
            link += "\'\'" + longtuderef

        else:
            msg = u'    Фото не содержит GPS-координат\n    Попробуйте другое фото'
            mb.showerror("Предупреждение", msg)
            link = None

        return link

    @staticmethod
    def open_brow(link):
        if link is not None:
            webbrowser.open(link)

    @staticmethod
    def device_information_link(tags, data_tags):
        link = "https://www.google.ru/search?q="
        i = 0

        for item in tags:
            if item == "make":
                link += str(data_tags[i])
            i += 1
        i = 0

        for item in tags:
            if item == "model":
                link = link + '+' + str(data_tags[i])
            i += 1

        if len(link) > len("https://www.google.ru/search?q=+"):
            return link
        else:
            msg = u'    Фото не содержит информацию об устройстве\n    Попробуйте другое фото'
            mb.showerror("Предупреждение", msg)
            return None

    @staticmethod
    def make_qr(link):
        if link is not None:
            qrcodename = fd.asksaveasfile(mode="wb", title="Сохранить файл",
                                          defaultextension=".png", filetypes=((".png", "*.png"),))
            if qrcodename:
                img = qrcode.make(link)
                img.save(qrcodename)
        else:
            msg = u'    Фото не содержит GPS-координат\n    Попробуйте другое фото'
            mb.showerror("Предупреждение", msg)

    def clean_and_save(self):
        self.photo.delete_all()
        path = fd.asksaveasfile(mode="wb", title="Сохранить файл",
                                defaultextension=".jpg", filetypes=((".jpg", "*.jpg"),))
        if path is not None:
            path.write(self.photo.get_file())

    def make_it_beautiful(self):

        tags, data_tags, filename = self.get_exif()

        if tags is not None and data_tags is not None:
            #   destroy greeting buttons
            self.btn_file.destroy()
            self.greeting.destroy()
            self.warning.destroy()
            self.img_label.destroy()
# __________________________________________________________________________________________________________
            #   set uploaded image + maybe header (nope, no header are permitted here!)
            image2 = Image.open(filename)
            width, height = image2.size
            k = width // 175
            image2 = image2.resize((int(width / k), int(height / k)), Image.ANTIALIAS)
            image2 = ImageTk.PhotoImage(image2)
            label2 = Label(image=image2, bg='#383838')
            label2.image = image2
            label2.place(relx=.95, rely=.02, anchor="ne", relwidth=0.2, relheight=0.27, bordermode='outside')
# __________________________________________________________________________________________________________
            #   set text widget
            text_tags = tk.Text(bg="white", wrap="word")
            text_tags.place(relx=.05, rely=.05, relwidth=0.4, relheight=0.7, anchor="nw", bordermode='outside')
            scroll = tk.Scrollbar(command=text_tags.yview)
            scroll.place(relx=.45, rely=.05, anchor="nw", relheight=0.7, bordermode='outside')
            text_tags.config(yscrollcommand=scroll.set, cursor='arrow')
# __________________________________________________________________________________________________________
            #   set hyperlink
            link = "https://www.exif.org/Exif2-2.PDF"
            text_tags.insert('0.0', "Больше про метаданные exif можно прочитать тут\n\n")
            text_tags.tag_add('link1', 1.43, 1.47)
            text_tags.tag_config('link1', foreground="blue", underline=True)
            text_tags.tag_bind('link1', '<Button-1>', lambda x: MainMenu.open_brow(link))
            text_tags.tag_bind('link1', '<Enter>', lambda x: text_tags.config(cursor='hand2'))
            text_tags.tag_bind('link1', '<Leave>', lambda x: text_tags.config(cursor='arrow'))
# __________________________________________________________________________________________________________
            #   set all tags
            for i in range(len(tags)):
                #   translator has '\n' already
                text = \
                    dict.translator(tags[i]) + '<' + tags[i] + '>' + '\n' + str(data_tags[i]) + '\n' + \
                    '_' * len(str(tags[i])) + '\n'
                text_tags.insert('{}.0'.format(3 + i * 6), text)
            text_tags.configure(state='disabled')
# __________________________________________________________________________________________________________
            #   set buttons (more buttons to the god of buttons)
            self.btn_file = tk.Button(self, text="Очистить метаданные и\nсохранить фото", bg='#454545', fg='#D1D1D1',
                                      font=('Arial', 12), relief="ridge", command=lambda: MainMenu.clean_and_save(self))
            self.btn_file.place(relx=.05, rely=.8, anchor="nw", relwidth=0.4, relheight=0.15, bordermode='outside')

            self.btn_file = tk.Button(self, text="Открыть\nгеолокацию", bg='#454545', fg='#D1D1D1',
                                      font=('Arial', 11), relief="ridge",
                                      command=lambda: MainMenu.open_brow(MainMenu.get_link(tags, data_tags)))
            self.btn_file.place(relx=.55, rely=.32, anchor="nw", relwidth=0.195, relheight=0.1, bordermode='outside')

            self.btn_file = tk.Button(self, text="Информация\nоб устройстве", bg='#454545', fg='#D1D1D1',
                                      font=('Arial', 11), relief="ridge",
                                      command=lambda: MainMenu.open_brow(
                                          MainMenu.device_information_link(tags, data_tags)))
            self.btn_file.place(relx=.755, rely=.32, anchor="nw", relwidth=0.195, relheight=0.1, bordermode='outside')

            self.btn_file = tk.Button(self, text="Сохранить геолокацию как QR-код", bg='#454545', fg='#D1D1D1',
                                      font=('Arial', 12), relief="ridge",
                                      command=lambda: MainMenu.make_qr(MainMenu.get_link(tags, data_tags)))
            self.btn_file.place(relx=.55, rely=.45, anchor="nw", relwidth=0.4, relheight=0.1, bordermode='outside')

            self.btn_file = tk.Button(self, text="Сохранить метаданные в файл", bg='#454545', fg='#D1D1D1',
                                      font=('Arial', 12), relief="ridge",
                                      command=lambda: MainMenu.save_to_file(tags, data_tags))
            self.btn_file.place(relx=.55, rely=.58, anchor="nw", relwidth=0.4, relheight=0.1, bordermode='outside')

            self.btn_file = tk.Button(self, text="Выбрать другое фото и\nпоказать метаданные", bg='#454545',
                                      fg='#D1D1D1',
                                      font=('Arial', 12), relief="ridge",
                                      command=lambda: MainMenu.make_it_beautiful(self))
            self.btn_file.place(relx=.55, rely=.71, anchor="nw", relwidth=0.4, relheight=0.1, bordermode='outside')

            self.btn_file = tk.Button(self, text="ВЫХОД", bg='#B8B8B8', fg='#383838',
                                      font=('Arial', 12), relief="ridge", command=self.destroy)
            self.btn_file.place(relx=.95, rely=.85, anchor="ne", relwidth=0.2, relheight=0.08, bordermode='outside')


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
