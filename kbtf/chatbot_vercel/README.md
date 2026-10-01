# 🚀 K-BTF 민원 챗봇 Vercel 원클릭 배포 가이드

## 🌐 1. Vercel CLI로 10초 만에 실시간 URL 생성하기
터미널에서 아래 명령어를 실행하면 `https://kbtf-civil-chatbot.vercel.app` 과 같은 무료 라이브 웹 URL이 즉시 생성됩니다:

```bash
cd /home/tomkim/mywork/kbtf/chatbot_vercel
npx vercel --prod
```
*(첫 실행 시 이메일 인증 또는 깃허브 로그인 안내 링크가 터미널에 출력됩니다)*

---

## 🌐 2. Vercel 웹 대시보드(vercel.com)에서 배포하기
1. [vercel.com](https://vercel.com)에 로그인
2. **`Add New...`** ➔ **`Project`** 클릭
3. 이 폴더(`/home/tomkim/mywork/kbtf/chatbot_vercel`)를 업로드하거나 GitHub에 푸시 후 선택
4. **`Deploy`** 버튼 클릭 시 즉시 배포 완료!
