from paramiko import SSHClient, AutoAddPolicy
import asyncio
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup

async def redustribute_license(host:str, password:str, user_name:str, license_path:str, dm_name:str):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            username=user_name, 
            password=password, 
            allow_agent=False, 
            look_for_keys=False
            )
        channel = client.get_transport().open_session()
        channel.get_pty()
        channel.settimeout(5)
        print('Подключение SSH выполнено успешно')
        sftp_client = client.open_sftp()
        sftp_client.put(license_path, '/root/auto_sa.cer')
        await asyncio.sleep(15)
        print('ЦА доставлен')
        channel.exec_command('cert_mgr import -f auto_sa.cer -t\n')
        print(channel.recv(1024).decode('utf-8'))
        print('Импорт завершен')
        with open('success_update.txt', 'ab') as f:
            f.write('Обновление {} ------> {}\n'.format(dm_name, 'Success').encode('utf-8'))
            f.close()
    except Exception as e:
        with open('success_update.txt', 'ab') as f:
            f.write('Обновление {} ------> {}\n'.format(dm_name, 'Faild').encode('utf-8'))
            f.close()

async def main():
    Tk().withdraw()
    input('Загрузите список хостов S-terra:\nДля продожения нажмите любую клавишу.')
    hosts_html = askopenfilename()
    input('Выберите файл лицензии корневого центра:\nДля продожения нажмите любую клавишу.')
    license_path = askopenfilename()
    user = input('Введите пользователя: ')
    passwd = input('Введите пароль: ')
    succ_file = open('success_update.txt', 'wb')
    succ_file.write(' '.encode('utf-8'))
    with open(hosts_html, 'rb') as f:
        tmp = f.read()
        soup = BeautifulSoup(tmp, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        hosts = []
        for row in rows:
            cols = row.find_all('td')
            cols = [val.text.strip() for val in cols]
            hosts.append(cols)
        f.close()
        tasks = []
        for host in hosts:
            print(f'Поставлен на обновление: {host[1]}, ip: {host[2]}')
            task = asyncio.create_task(redustribute_license(
                host=host[2],
                password=passwd,
                user_name=user,
                license_path=license_path,
                dm_name=host[1]
            ))
            tasks.append(task)
        await asyncio.wait(tasks)
        print('Обновление завершено.\nРезультаты смотрите в файле success_update.txt\n')
        input('Для завершения нажмите любую клавишу')

asyncio.run(main())

