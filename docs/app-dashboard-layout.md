# /app main page — dashboard layout (first-pass)

> Related issue: #471
> Related epics: #406 (heatmap-ui-system), #424 (mobile quick log UI)

---

## 1. Why

`#406` と `#424` はどちらも `/app` main page を対象とするが、両者がページ上でどう共存するかは未定義のままだった。
実装が進むにつれてレイアウトがコードで暗黙に固定されるリスクがあるため、
実装開始前にページレベルの骨格を明文化する。

---

## 2. Page layout decision

`/app` main page の first-pass layout は以下の単一カラム縦スタックとする。

```
[ heatmap area      ]   ← 上部
[ quick log area    ]   ← 下部
```

- 単一カラムを採用する
- 横並び・2カラム化は first-pass のスコープ外

---

## 3. Rationale

- **heatmap area は観測文脈の導入として機能する。** ページに到達した時点で、ユーザーは過去の記録の概要を視野に入れた状態になる。
- **quick log area はその文脈を受けて入力を行う主アクション領域。** 観測 → 行動という認知順序を優先する。
- heatmap が上部にあることは quick log の重要性を損なわない。heatmap はあくまで導入として機能し、quick log は常に到達可能な主操作として位置づける。

---

## 4. Mobile-first policy

- モバイルが主対象。
- heatmap を先に置くが、**quick log を過度に押し下げない**。
- first-pass では heatmap area は summary-oriented かつ compact な導入として実装することを前提とする。heatmap の高さは quick log への到達性と釣り合いが取れる範囲に収める。
- ページ全体のスクロールなし保証はこの doc のスコープ外。quick log に到達しやすいことを方針として示すにとどめる。

---

## 5. Desktop first-pass policy

- desktop でも first-pass では mobile と同じ情報階層を維持する。
- first-pass では縦スタックを採用し、heatmap → quick log の順序は変えない。
- 2カラム化や画面幅に応じた再配置は将来の検討事項であり、この doc のスコープ外。

---

## 6. Area ownership / responsibility boundaries

この doc はページレベルの構成のみを扱う。各エリアの内部 UI 設計は子 issue に委ねる。

| エリア | 内部設計の担当 |
|--------|----------------|
| quick log area | #424 および子 issue (#425–#428) |
| heatmap area | #406 および子 issue (#390, #391 等) |

**この doc の責務はエリアの配置のみ。** 以下については子 issue が決定する:

- quick log area: 入力モード (quick/tag/text) の構成・候補 UI・補助文言・フィードバック表現
- heatmap area: 可視化仕様・凡例・バケット表現・説明・操作詳細

---

## 7. Non-scope

- quick log 内部 UI の詳細設計
- heatmap 内部 UI の詳細設計（パレット・凡例・日詳細パネル等）
- `/dashboard` から `/app` への機能移行手順・カットオーバータイミング
- デスクトップ最適化の詳細・2カラム化
- 候補 UI の並び順や補助文言
- 実装順序の厳密な固定

---

## 8. Relationship to downstream issues

- **#424 サブ issue** (#425–#428 等) は quick log area 内の設計・実装を担う。本 doc はそれらに対して「quick log area は heatmap area の下に配置される」という前提を提供する。
- **#406 サブ issue** (#390, #391 等) は heatmap area 内の設計・実装を担う。本 doc はそれらに対して「heatmap area はページ上部の導入として compact に実装する」という方針を提供する。
- 下流 issue は本 doc をページレベルのレイアウト前提として参照できる。

---

## 9. Difference from existing `/dashboard` layout docs

`docs/daily-input-ux-mvp.md` には、現行 `/dashboard`（vanilla JS）における以下のレイアウト原則が含まれている。

```
[ Grass Heatmap (28 days)    ]   ← Top fixed
[ Candidate Tags (one-tap)   ]   ← Below heatmap
[ Free-text Input Field      ]   ← Below tags
```

この構成と `/app` における本 doc の構成は、認知順序として heatmap を先に置くという考え方で整合している。

ただし、両者の文書の対象と粒度は異なる:

- `docs/daily-input-ux-mvp.md` は現行 `/dashboard` 文脈のレイアウト原則であり、候補 UI や text UI を含む細かな並び順まで含んでいる。
- 本 doc は `/app` における **ページレベルのエリア構成**（heatmap area / quick log area の配置）のみを定義する。候補 UI や text UI の並び順の再定義はスコープ外であり、それらは #424 系に委ねる。
