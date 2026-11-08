# Status | 마지막: 2026-11-09
## 현재 작업
AdSense 승인 가능성 개선 완료(코드 측). 재신청 전 사용자 작업 대기.
## 최근 변경 (최근 5개만)
- 11-09: 필명 편집자(Alex Morgan, 가제) About·글 JSON-LD author Person 적용
- 11-09: About 페이지 히어로 이미지 + alt 추가
- 11-09: 템플릿형 "Practical next step" 96개 글별 고유 문단으로 교체
- 11-08: AdSense pub ID → ca-pub-7865675606131621, ads.txt 교체
- 11-08: author/publisher JSON-LD에 About URL 연결, .omc/ git 제외
## TODO
- [ ] AdSense 대시보드 Privacy & messaging에서 EEA/UK 동의 메시지 켜기 (사용자)
- [ ] 크롤링 대기 후 AdSense 재신청, ads.txt 인식 확인 (사용자)
- [ ] 실명 편집자 정보 확정 시 `Alex Morgan` 일괄 치환 + About 문구 수정
## 결정사항
- 편집자는 필명(가제): 허위 자격 표기는 정책 위험이라 경력 미기재
- 배포: git push → Contabo `dogbreed-updater.timer`(10분 폴링) 자동 반영
## 주의
- 글에 이미지 없음(About만 있음). 보더콜리 글 next-step은 기존 커스텀 유지
- lint/build 직접 실행 금지, grep/curl로 검증
