# Follow-Up Questions — Architecture Change

Q3 답변에서 **서버리스(Firebase/Lambda) 대신 EC2/S3 기반 서버 배포**로 전환하신다는 점을 확인했습니다.
원래 아키텍처 문서와 상당한 차이가 있어 추가 확인이 필요합니다.

---

## FQ1. 백엔드 프레임워크

EC2에서 운영할 백엔드 서버 프레임워크는 무엇을 사용하시겠습니까?

- A) Node.js + Express
- B) Node.js + NestJS
- C) Python + FastAPI
- D) Python + Django
- E) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## FQ2. 인증 방식 (Q3 재확인)

Firebase 대신 EC2 서버 기반이라면 인증을 어떻게 처리하시겠습니까?

- A) AWS Cognito (AWS 관리형 인증 서비스)
- B) 자체 구현 (JWT 기반 이메일/비밀번호 인증)
- C) Passport.js + 소셜 로그인 (Google, Kakao 등)
- D) 자체 JWT + Google OAuth만
- E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## FQ3. 데이터베이스

Firebase Firestore 대신 어떤 DB를 사용하시겠습니까?

- A) AWS RDS (PostgreSQL)
- B) AWS RDS (MySQL)
- C) MongoDB (EC2에 직접 설치 또는 Atlas)
- D) DynamoDB (AWS 관리형 NoSQL)
- E) Other (please describe after [Answer]: tag below)

[Answer]:  A

---

## FQ4. 파일 저장소

사용자 이미지(전신 사진, 의류 이미지, 생성 결과) 저장은?

- A) AWS S3 (Signed URL로 접근 제어)
- B) EC2 로컬 디스크 + Nginx 정적 파일 서빙
- C) S3 + CloudFront CDN
- E) Other (please describe after [Answer]: tag below)

[Answer]: E (민감 사용자 정보 라서 클라우드 저장소에 저장하는것은 지양, 서버에서는 휘발성으로 존재하고 사용자가 로컬에 저장할 수 는 있도록 해줘)

---

## FQ5. 프론트엔드 배포 방식

React 앱 배포를 EC2에서 함께 서빙하시겠습니까?

- A) EC2 Nginx에서 프론트엔드 정적 파일도 함께 서빙 (단일 서버)
- B) S3 + CloudFront로 프론트엔드 별도 호스팅, EC2는 API 서버만
- C) EC2에서 Node.js로 프론트+백엔드 모두 서빙
- E) Other (please describe after [Answer]: tag below)

[Answer]: B

---

답변 후 Requirements Document를 생성하고 다음 단계로 진행하겠습니다.
