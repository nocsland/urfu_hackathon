cd ..
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
sed '$d' one_click.py > one_click_install.py
mv one_click.py one_click_old.py
mv one_click_install.py one_click.py 
export GPU_CHOICE="A"
export USE_CUDA118="Y"
./start_linux.sh
cd models
wget https://huggingface.co/TheBloke/openchat_3.5-GGUF/resolve/main/openchat_3.5.Q8_0.gguf
cp ../../urfu_hackathon/config/settings.yaml .
cp ../../urfu_hackathon/config/config-user.yaml .
cd ..
mv one_click.py one_click_.py
mv one_click_old.py one_click.py
cd ..
