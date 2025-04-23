import os
import pytubefix
import ffmpeg
import google.generativeai as genai
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from pathlib import Path
import threading

# Configuração da API
genai.configure(api_key="SUA API IA")

# Diretório de downloads
DOWNLOAD_DIR = Path.home() / "Downloads"

# Função para processar o link do YouTube
def process_youtube_link(url, file_format, progress_bar):
    if url:
        filename = "audio.wav"

        try:
            progress_bar.pack(pady=10, fill='x')  # Mostrar a barra de progresso quando o processamento começa
            progress_bar.start()
            yt = pytubefix.YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()

            if audio_stream:
                audio_stream.download(filename="temp_audio.mp4")
                ffmpeg.input("temp_audio.mp4").output(filename, format='wav').overwrite_output().run()

                audio_file = genai.upload_file(filename)

                model = genai.GenerativeModel(model_name="gemini-1.5-flash")

                prompt_transcription = "Transcreva o áudio do seguinte arquivo e gere o texto completo."
                response_transcription = model.generate_content([prompt_transcription, audio_file])

                transcribed_text = response_transcription.text

                prompt_summary = (
                    "A partir do seguinte texto transcrito, faça um resumo, "
                    "identifique as teses principais e destaque os tópicos importantes"
                    "OBS. troque todo e qualquer valor numerico por expreções, não quero nenhum número, seja data tamanho ou quantidade: "
                    + transcribed_text
                )
                response_summary = model.generate_content([prompt_summary])

                summary_text = response_summary.text

                # Salvar o resumo no formato escolhido pelo usuário na pasta de downloads
                save_path = DOWNLOAD_DIR / f"{yt.title}.{file_format}"
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(summary_text)
                messagebox.showinfo("Resumo Salvo", f"Resumo salvo em: {save_path}")

            else:
                messagebox.showwarning("Erro", "Nenhum stream de áudio disponível.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
        finally:
            progress_bar.stop()
            progress_bar.pack_forget()  # Esconder a barra de progresso quando o processamento terminar
    else:
        messagebox.showwarning("Erro", "Nenhum link foi inserido.")

# Função para adicionar uma nova caixa de texto
def add_link_entry():
    new_entry = tk.Entry(link_frame, width=50, font=("Helvetica", 10))
    new_entry.pack(pady=5)
    link_entries.append(new_entry)

# Função para processar todos os links inseridos
def process_all_links():
    file_format = format_var.get()
    if not file_format:
        messagebox.showwarning("Aviso", "Por favor, selecione um formato para salvar o resumo.")
        return
    
    for entry in link_entries:
        link = entry.get()
        if link:
            thread = threading.Thread(target=process_youtube_link, args=(link, file_format, progress_bar))
            thread.start()
        else:
            messagebox.showwarning("Aviso", "Um dos campos de link está vazio. Por favor, insira um link válido ou remova o campo.")

# Interface Gráfica
root = tk.Tk()
root.title("Resumidor de Vídeos do YouTube")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# Frame para os links
title_label = tk.Label(root, text="Resumidor de Vídeos do YouTube", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
title_label.pack(pady=15)

link_frame = tk.Frame(root, bg="#f0f0f0")
link_frame.pack(pady=15)

link_entries = []

# Caixa de texto inicial
initial_entry = tk.Entry(link_frame, width=50, font=("Helvetica", 10))
initial_entry.pack(pady=5)
link_entries.append(initial_entry)

# Botão para adicionar mais caixas de texto
add_button = tk.Button(root, text="Adicionar mais um link", command=add_link_entry, font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
add_button.pack(pady=10)

# Opções de formato de arquivo
format_var = tk.StringVar(value="txt")
format_label = tk.Label(root, text="Selecione o formato para salvar o resumo:", font=("Helvetica", 12), bg="#f0f0f0")
format_label.pack()
format_options = ["txt", "pdf", "docx"]
format_menu = tk.OptionMenu(root, format_var, *format_options)
format_menu.config(font=("Helvetica", 12))
format_menu.pack(pady=10)

# Barra de progresso
progress_bar = ttk.Progressbar(root, mode='indeterminate')

# Botão para processar todos os links
process_button = tk.Button(root, text="Processar Links", command=process_all_links, font=("Helvetica", 14, "bold"), bg="#2196F3", fg="white", padx=15, pady=10)
process_button.pack(pady=20)

# Mensagem no rodapé
footer_label = tk.Label(root, text="O resumidor pode cometer erros. Revise o texto antes de considerar.", font=("Helvetica", 10), fg="red", bg="#f0f0f0")
footer_label.pack(side="bottom", pady=10)

root.mainloop()
