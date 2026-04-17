from bing_image_downloader import downloader

downloader.download("people street", limit=50, 
    output_dir=r"C:\Users\ADMIN\Desktop\explainbleAI-Project\project\dataset\train\non_endoscopy")

downloader.download("cars road", limit=50, 
    output_dir=r"C:\Users\ADMIN\Desktop\explainbleAI-Project\project\dataset\train\non_endoscopy")

downloader.download("buildings city", limit=50, 
    output_dir=r"C:\Users\ADMIN\Desktop\explainbleAI-Project\project\dataset\train\non_endoscopy")

downloader.download("animals", limit=50, 
    output_dir=r"C:\Users\ADMIN\Desktop\explainbleAI-Project\project\dataset\train\non_endoscopy")