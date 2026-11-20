# 調査メモ: 漫画の絵柄から「素人っぽさ」を抜く方法

調査日 2026-11-20。各項目の後ろに、スキルのどこに反映したかを書く。

## 線画
- 線の太さが均一だと、のっぺり見える。始まりと終わりを細くする「入り抜き」で線に表情を付ける。
  → `taper()`、ルール1
- 光源を決め、光の当たりにくい側の輪郭を太くすると、影と量感が出る。主役キャラの線は太めにする。
  → `contour(light_k)`、ルール2
- 線を何度も重ねたり、消して描き足したりすると継ぎ目ができて汚く見える。一筆で引ける線は一度で引く。
  → 1本1パスの原則、`bubble()` のしっぽ一体化
- 可変幅の線の実装方法: 中心線をサンプリングし、各点の幅の半分だけ法線方向へ両側にずらして、多角形として閉じる(Inkscape の Power Stroke と同じ考え方)。
  → `taper()` / `contour()` の実装

## 髪
- 頭の丸みを意識し、生え際やつむじから放射状に描く。つむじや分け目にガイドを置くと、毛の分割が決めやすい。
  → 分け目の点から放射する `clump(profile='leaf')`
- 全部を描かず、束として省略する。大きな影を見つけることが大事。
  → 毛束ごとの影トーン
- 前髪の幅は両眉の端あたりが目安。
  → 前髪の配置

## トーン・影
- まず光源の方向を決め、光が遮られる側に影を置く。
- 固有色のトーン(ベース)の上に、影トーンを重ねる(2段)。
  → ルール4
- 影の縁を少し残すとパーツが分かれ、奥行きが出る。

## 顔のバランス
- 標準の顔では目は顔の高さの中央付近で、目と目の間は目1つ分。幼く描くならパーツを下・中央に寄せ、目を大きくする。
- 目を左右対称にすると動きが無くなる。初心者は両目を近づけすぎがち。
  → ルール5、頭の傾き `rot`

## 写植
- 漫画のセリフには、明朝体のかなとゴシック体の漢字を組み合わせた「アンチック体」(アンチゴチ)が使われる。
  → CSS の `unicode-range` で Noto Serif のかなと Noto Sans の漢字を合成した `ANTIQUE`
- 写植の指定(書体、サイズ、配置)は読みやすさと没入感を左右する演出の一部。

## 出典
- [ココナラ: 線に命を吹き込む"入り"と"抜き"](https://coconala.com/blogs/5616558/636301)
- [CLIP STUDIO TIPS: Tips when drawing line art for animation(入り抜き)](https://tips.clip-studio.com/en-us/articles/957)
- [CLIP STUDIO お絵かき講座: 線画](https://www.clipstudio.net/oekaki/archives/153211)
- [CLIP STUDIO お絵かき講座: 線の強弱と光源](https://www.clipstudio.net/painting/archives/164780)
- [CLIP STUDIO お絵かき講座: 髪の描き方](https://www.clipstudio.net/oekaki/archives/152318)
- [髪の描き方(省略と影)](https://www.asahi-net.or.jp/~zm5s-nkmr/hitoFiles/hair7.html)
- [CLIP STUDIO お絵かき講座: 光と影](https://www.clipstudio.net/oekaki/archives/152356)
- [CLIP STUDIO TIPS: SHADING AND TEXTURES](https://tips.clip-studio.com/en-us/articles/4256)
- [CLIP STUDIO お絵かき講座: 顔のバランス](https://www.clipstudio.net/oekaki/archives/156114)
- [顔のパーツの配置](https://www.asahi-net.or.jp/~zm5s-nkmr/hitoFiles/kaonoprtu.html)
- [GIGAZINE: やさしいアンチック](https://www.gigazine.net/news/20131205-yasashisa-antique-font/)
- [窓の杜: 源暎アンチック](https://forest.watch.impress.co.jp/docs/review/721966.html)
- [ファミ通: 写植指定AI](https://www.famitsu.com/article/202604/72091)
- [W3C www-svg: variable-width strokes の議論(Power Stroke)](https://lists.w3.org/Archives/Public/www-svg/2013May/0007.html)
