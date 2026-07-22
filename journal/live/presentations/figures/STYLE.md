# Figure house style — greyscale, paper register

Every figure in this set obeys this. With no colour available, **all distinction is carried by
stroke weight, dash pattern, and hatching** — so the vocabulary below is fixed and must not drift.

## Stroke weights — exactly three

| Weight | Meaning |
|---|---|
| `1.6` | the **load-bearing path** — exactly one per figure |
| `1.0` | structure: boxes, ordinary edges, axes |
| `0.6` | context, de-emphasis, hatch lines, tick marks |

If a figure seems to need a fourth weight, it is doing two jobs and should be split.

## Dash patterns

| Pattern | Meaning |
|---|---|
| solid | actual / committed / the path taken |
| `stroke-dasharray="4 2"` | the alternative not taken |
| `stroke-dasharray="1 2"` | **absent / refused** — always paired with `fill="none"` |

## Enclosure — the exception, not the default

**Boxes are the failure mode of technical figures.** A grid of bordered rectangles reads as an org
chart. Default instead to **bare labels**: an object is its name, set in type, surrounded by
whitespace. Draw a boundary only when the boundary itself carries meaning.

| Form | Use |
|---|---|
| **bare label** | an object in a diagram of objects and maps — **the default** |
| **ellipse / circle** | an *operation*, something applied — soft-edged |
| **segmented strip** | *data with parts*, where completeness or absence is the point |
| **curly brace** | grouping a list without drawing a container around it |
| **hairline rule** (`0.6`, `#cccccc`) | separating rows or panels — instead of nesting |
| **soft fill, no stroke** | a region or domain, where the extent matters but the edge does not |

Bordered rectangles are reserved for the rare case where something genuinely *is* a container.
**Never nest one rectangle inside another.** If a figure contains more than two rectangles *acting
as enclosures*, it is almost certainly wrong.

(Segments of a strip are not enclosures — they are one datum drawn in parts, and a strip may have
as many segments as it has channels. The thing being counted is containers, not `<rect>` elements.)

Whitespace is a drawing tool. Generous margins and clear baselines do more structural work than
any border.

## Arrow geometry — carries meaning

| Form | Meaning |
|---|---|
| **curved** — quadratic Bézier, sagitta ≈ 8–12% of chord | a **morphism between abstract objects**; relationship and data flow. The commutative-diagram register. Label sits outside the arc. |
| **straight / orthogonal** | genuine **program or control flow**, *and* any structure carrying an established drawing convention |

Straight is **mandatory**, not merely permitted, for **BDD edges, Hasse diagrams, and Merkle
DAGs**. Those notations are conventionally straight; bending them reads as an error to anyone who
knows them.

Curved arrows are `<path d="M … Q … …">` with `fill="none"` — never `<line>`. For a chord of
length `L`, place the control point about `0.2 L` along the outward normal from the chord
midpoint; that yields a sagitta of about `0.1 L`.

Per-figure: **curved** — F2, F3, F4, F5, F6, F8, F12. **Straight** — F1 (chart),
F7 (program flow), F9 (chart), F10 (BDD convention), F11 (Hasse + DAG convention).

Note that a curly brace is drawn with `Q` segments but is *not* an arrow; a straight-arrow figure
may legitimately contain one (F7 does).

## Fills — five values, no others

`#ffffff` · `#eeeeee` · `#cccccc` · `#999999` · `#000000`

Four tints is the ceiling; beyond that adjacent regions stop being distinguishable in print.

## Hatching

45° diagonal hatch = **expensive / intractable** region. Blank = cheap. One pattern only.

## Type — small, three sizes

- One family: `Charter, Georgia, 'Times New Roman', serif`.
- **`12`** headline object · **`9`** label · **`8`** gloss and caption (italic). Nothing else.
- Type should feel small against the frame. If a figure reads as a poster rather than a plate in
  a paper, the type is too big or the spacing too loose.
- No bold anywhere except the single emphasised element. Sentence case throughout.

## Content — earn the figure

A figure must carry information the sentence beneath it cannot. Specifically **do not draw**:

- **positioning charts** — 2×2s, quadrant diagrams, "X vs Y" scatters with two labelled points.
  They encode almost nothing and read as condescending to a technical audience.
- **pipelines of labelled boxes** where the labels *are* the content. Say it in a sentence.

Prefer the actual mathematical object: **sets and containments**, **derivation / syntax trees**,
**lattices**, **decision diagrams**, **DAGs**, **matrix structure**. If the underlying idea has a
standard picture in its own field, draw that picture.

## Caption

Inside the SVG, beneath the frame, left-aligned:
`Figure N. <one sentence>.` — italic, `10px`, `#000`.
Keeping the caption in the file means the figure travels self-contained into any deck.

## Geometry and portability

- `viewBox` on every file; **no** `width`/`height` attributes (so it scales into any slide).
- No external references, no embedded raster, no `<style>` blocks depending on inherited CSS.
- Must render standalone in a browser and survive import into a deck unchanged.

## Forbidden

Gradients · shadows · blur · rounded corners > 2px · decorative arrowheads · icons · emoji ·
colour of any kind.

## Shared `<defs>` — paste into every figure

```svg
<defs>
  <marker id="a" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="#000000"/>
  </marker>
  <pattern id="hatch" width="6" height="6"
           patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
    <line x1="0" y1="0" x2="0" y2="6" stroke="#999999" stroke-width="0.6"/>
  </pattern>
</defs>
```

## The one rule that must not drift

Every `fill=` and `stroke=` value is one of the five permitted greys, `none`, or `url(#hatch)`.
Anything else is a defect. This is mechanically checkable — do check it.
