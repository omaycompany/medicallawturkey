import os
import glob

files = glob.glob('/Users/busraocak/Desktop/Medicallaw Turkeyy/*.html')

injection = """  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v=20260901-nav">
  <link rel="icon" href="favicon.ico" type="image/x-icon">
  <link rel="apple-touch-icon" href="images/logo.png">
"""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if "styles.css" not in content:
        new_content = content.replace("</head>", injection + "</head>")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print("Fixed", f)
