# Инструкция по загрузке в GitHub

## Способ 1: Через SSH ключ (рекомендуется)

1. Создайте SSH ключ:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Добавьте ключ в GitHub:
- Скопируйте содержимое ~/.ssh/id_ed25519.pub
- Перейдите в GitHub Settings > SSH and GPG keys
- Добавьте новый SSH ключ

3. Измените remote URL:
```bash
git remote set-url origin git@github.com:vinnienasta1/wg-easy-tg.git
```

4. Загрузите проект:
```bash
git push -f origin main
```

## Способ 2: Через Personal Access Token

1. Создайте Personal Access Token в GitHub:
- Settings > Developer settings > Personal access tokens > Tokens (classic)
- Выберите scope: repo

2. Загрузите проект:
```bash
git push -f origin main
# Username: vinnienasta1
# Password: ваш Personal Access Token
```

## Способ 3: Через GitHub CLI

1. Установите GitHub CLI:
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

2. Авторизуйтесь и загрузите:
```bash
gh auth login
git push -f origin main
```

## Проверка загрузки

После загрузки проверьте:
- https://github.com/vinnienasta1/wg-easy-tg
- Все файлы должны быть на месте
- README.md должен отображаться корректно
