FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y wget curl unzip gnupg && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && apt-get update && apt-get install -y google-chrome-stable
COPY . .
CMD ["python", "bot123.py"]
