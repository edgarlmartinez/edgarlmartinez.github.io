---
number: 2
title: MRI is fat and water
subtitle: Fat is the canvas, water is the messenger
status: draft
summary: The basic MRI concepts for MSK, built on one idea. T1 shows fat, fluid-sensitive images show water, and almost every MSK diagnosis is fat that has disappeared or water in the wrong place.
updated: 2026-11
---

MRI physics fills whole textbooks. For musculoskeletal reading, you can go a very long way with one idea:

> **Every MSK MRI is a story about fat and water.** On T1-weighted images, fat is bright and water is dark. On fluid-sensitive images (T2, proton density with fat suppression, STIR), water is bright. Disease either **removes fat** (tumor, infection, marrow replacement) or **puts water where it should not be** (edema, tears, fluid collections).

If you look at every sequence by asking "where is the fat, and where is the water?", the sequences stop being a list of acronyms and become two questions you already know how to answer.

<figure>
  <img src="/book/figures/fat-water.svg" alt="Grid of schematic gray levels: fat bright on T1 and T2 and dark on fat-suppressed images; water dark on T1 and bright on T2 and fat-suppressed images; replaced marrow dark on T1 and bright on fluid-sensitive images; muscle intermediate; tendons, ligaments, menisci and cortex dark on all." />
  <figcaption>Figure 2.1. How the main tissues look on the three sequences you will read most. Schematic.</figcaption>
</figure>

## 2.1 The sequences, in one table

| Sequence | Fat | Water | Use it to answer |
| --- | --- | --- | --- |
| **T1** | Bright | Dark | Anatomy. Is the marrow fat still there? Is a mass fatty? Is there a fracture line? |
| **T2 (fast spin echo)** | Bright | Bright | Fluid and cysts, without fat suppression. |
| **Fat-suppressed T2 or PD** | Dark | Bright | Edema, tears, fluid, cartilage (PD). The workhorse of sports imaging. |
| **STIR** | Dark | Bright | Edema over large areas or near metal, where fat suppression fails. Very sensitive, not specific. |
| **Proton density (PD)** | Intermediate–bright | Intermediate | Menisci, labrum, cartilage: high signal-to-noise and fine detail. |
| **In-phase / opposed-phase (chemical shift, Dixon)** | Signal drops on opposed-phase when fat and water share a voxel | | Is there fat mixed into this marrow? |
| **T1 fat-suppressed after gadolinium** | Dark | Enhancing tissue bright | Abscess versus phlegmon, viable versus necrotic tumor, synovitis. |

Why do we suppress fat at all? Because in MSK, **fat is everywhere** (marrow, subcutaneous tissue, intermuscular planes, Hoffa's fat pad). Bright fat on a T2 image hides bright water. Remove the fat and every bit of water lights up.

## 2.2 Fat is the canvas

In adults, most of the appendicular marrow is **yellow (fatty) marrow**, so the marrow is bright on T1, almost as bright as subcutaneous fat. Red (hematopoietic) marrow persists in the axial skeleton and proximal femora and humeri, and it is darker, but it still contains a large amount of fat.

That fat is what tumor and infection consume. A useful way to say it to residents: **tumor and infection do not add a signal to the marrow, they take the fat away.** Cells, pus and edema displace and destroy the fat cells, and the bright T1 canvas turns dark.

### The internal reference: muscle and disc

You need a reference to decide whether marrow is "too dark". Use what is in the same image:

- **Normal marrow, red or yellow, is brighter than skeletal muscle** on T1 (in the spine, brighter than a normal intervertebral disc).
- **Marrow that is darker than muscle or disc on T1 has lost its fat.** That is marrow replacement until proven otherwise: tumor, myeloma, lymphoma, metastasis, or infection.

This one comparison, made on a T1 image, is the most valuable habit in MSK MRI. See it in the [sclerotic metastasis case](/cases/#sclerotic-met), where the lesion is dark on T1.

<div class="ex-slot" data-topic="marrow-replacement"></div>

### When fat is hidden: chemical shift imaging

Red marrow and marrow edema can look worrying on T1 and on STIR. Chemical shift imaging asks whether **fat is still mixed in with water in the same voxel**. On opposed-phase images, fat and water signals cancel each other, so a voxel that contains both **loses signal** compared with the in-phase image. Tumor that has replaced the fat does not lose signal.

- **Signal drop on opposed-phase**: fat is still there. Favors red marrow, edema or another benign process.
- **No signal drop**: the fat is gone. Favors marrow replacement by tumor.

In vertebral marrow, a signal-intensity ratio (opposed-phase divided by in-phase) **above 0.8, meaning a drop of less than 20%,** favored a malignant process (Zajick et al. 2005). Be careful with sclerotic lesions and in very cellular benign marrow, and use the ratio as one feature among several.

The PSMA-avid femoral lesion in the [educational cases](/cases/#psma-red-marrow) is the textbook example: the signal falls from about 259 on in-phase to about 27 on opposed-phase, a drop of about 90%. That is fat, and the lesion was focal red marrow, not metastasis.

<div class="ex-slot" data-topic="chemical-shift"></div>

### Fat is reassuring

Because tumor destroys fat, **macroscopic fat inside a bone lesion is usually a good sign**: intraosseous lipoma, typical vertebral hemangioma, the fatty center of a bone island or a healed lesion, a fat-containing ganglion. A lesion that keeps fat inside it is rarely aggressive. (In soft tissue, the exception you must remember is the well-differentiated liposarcoma: fat with thick septa or nodular non-fatty components.)

## 2.3 If you can only run one sequence: T1

A diabetic patient with a foot ulcer cannot lie still, or claustrophobia allows only a few minutes in the magnet. The clinician asks: is there osteomyelitis? **If you can run only one sequence, run T1.**

<figure>
  <img src="/book/figures/t1-osteomyelitis.svg" alt="Three schematic T1-weighted images of a bone: normal bright fatty marrow; reactive edema with a hazy reticulated pattern but preserved fat; and osteomyelitis with confluent dark medullary signal next to an ulcer, darker than muscle." />
  <figcaption>Figure 2.2. T1 marrow patterns in a suspected osteomyelitis. Only the confluent medullary pattern means the fat is gone.</figcaption>
</figure>

Why T1 and not STIR? Fluid-sensitive sequences are **very sensitive and poorly specific**: reactive marrow edema next to an ulcer (osteitis), stress reaction, recent surgery and neuropathic change all light up on STIR. T1 answers a sharper question: **has the infection destroyed the marrow fat?**

- **Osteomyelitis**: confluent, low T1 signal in a **medullary** distribution, darker than skeletal muscle, contiguous with the ulcer or sinus tract. In one series of foot MRIs, this pattern had a sensitivity of 95% and specificity of 91% for osteomyelitis, with a negative predictive value of 98% (Johnson et al. 2009).
- **Reactive edema or osteitis**: a hazy, reticulated or only subcortical T1 pattern, with fat still visible between the abnormal areas. In the same series, these patterns did not correspond to osteomyelitis.
- **STIR bright, T1 normal**: edema without fat destruction. Not osteomyelitis on this study.

**Pitfalls.** Neuropathic (Charcot) joints, fractures, recent surgery, and tumor can also make T1 dark. Location helps: osteomyelitis in the diabetic foot spreads from the skin, so it sits under an ulcer, at the pressure points (metatarsal heads, toes, calcaneus, the cuboid in rocker-bottom foot). Neuropathic change is periarticular and centered on the midfoot joints, often without an ulcer.

<div class="ex-slot" data-topic="osteomyelitis"></div>

## 2.4 Water is the messenger

Collagen-rich structures are dark on every sequence: **tendons, ligaments, menisci, labra and cortex**. Their tightly ordered collagen has a very short T2, so they give almost no signal. That makes water easy to see against them.

The rule for tears: **a tear is water where water should not be.** Bright, fluid-like signal that enters a dark structure, separates its fibers, or fills a gap is a tear. Signal that is brighter than the normal structure but **less bright than fluid**, the in-between signal, usually means **degeneration** (mucoid or myxoid change), not a tear.

<figure>
  <img src="/book/figures/water-tears.svg" alt="Schematic meniscus: normal dark triangle, degeneration with intermediate signal not reaching a surface, and tear with bright linear signal reaching the articular surface. Schematic tendon: normal thin dark, tendinosis thickened with gray signal, partial tear with bright cleft, full-thickness tear with fluid-filled gap." />
  <figcaption>Figure 2.3. Gray is degeneration. White is water in the wrong place.</figcaption>
</figure>

### Meniscus

- **Normal**: a uniformly dark triangle (body) or bow tie.
- **Degeneration**: globular or linear intermediate signal **inside** the meniscus that **does not reach an articular surface**. Common with age, and not a surgical lesion.
- **Tear**: signal that **reaches the superior or inferior articular surface**, or an abnormal shape (a truncated, displaced or missing piece). The **two-slice-touch rule**: call a tear when the surface-reaching signal or abnormal shape is seen on two or more images; if it is seen on only one image, call it a possible tear. This raised the positive predictive value of the diagnosis, especially in the lateral meniscus (De Smet and Tuite 2006).
- **Look for the missing piece.** A flipped fragment in the intercondylar notch (double PCL sign) or a fragment in the gutter changes management.

<div class="ex-slot" data-topic="meniscus"></div>

### Ligaments

- **Sprain or tear**: fluid-bright signal around and through the fibers, loss of the normal straight dark band, and, in a complete tear, discontinuity with wavy or retracted ends.
- **Mucoid degeneration of the ACL**: the ligament is thickened and intermediate in signal, but its fibers are continuous, like a stalk of celery. It is degeneration, not a tear, and is a common false positive.
- **Look at the bones.** A ligament tear often leaves a bone bruise pattern (water in the marrow) that tells you the mechanism, such as the lateral femoral condyle and posterolateral tibial plateau in a pivot-shift ACL injury.

<div class="ex-slot" data-topic="ligament"></div>

### Tendons

- **Tendinosis**: a thickened tendon with **intermediate** signal on PD and T2, not as bright as fluid.
- **Partial-thickness tear**: a **fluid-bright** cleft that involves part of the tendon thickness or a surface.
- **Full-thickness tear**: a fluid-filled gap across the whole tendon, often with retraction. Measure the gap and say where the ends are; the surgeon needs it.

### The trap in the gray zone: the magic angle

Collagen fibers that run at about **55 degrees to the main magnetic field** can show increased signal on **short-TE sequences** (T1, PD, gradient echo) even when they are normal (Erickson et al. 1991). Classic sites: the supraspinatus tendon near its insertion, the peroneal and posterior tibial tendons as they curve around the malleoli, and the posterior horn of the lateral meniscus. **The signal disappears on long-TE (T2) images.** If an intermediate signal is present only on the short-TE image and the tendon is not thickened, think magic angle before you call tendinosis.

<div class="ex-slot" data-topic="tendon"></div>

## 2.5 Putting it together at the workstation

For every MSK MRI, read in this order:

1. **T1 first: where is the fat?** Is the marrow brighter than muscle everywhere? Are fat planes preserved around the joint and around any mass?
2. **Fluid-sensitive images: where is the water?** Edema in the marrow, fluid in the joint, fluid around or through a tendon, ligament or meniscus.
3. **Ask whether the water explains the fat.** Water with preserved T1 fat is usually edema, stress reaction or osteitis. Water with T1 fat loss is replacement: infection, tumor or fracture line.
4. **Grade the in-between signal.** Gray is degeneration; white is a tear.

<div class="never">

### Never forget

- On T1, normal marrow is brighter than muscle. Darker than muscle means the fat is gone.
- Tumor and infection take the fat away. Fat inside a bone lesion is usually reassuring.
- If you can run only one sequence for osteomyelitis, run T1. STIR is sensitive, T1 is specific.
- Opposed-phase signal drop means fat is present. No drop means the fat has been replaced.
- A tear is fluid-bright signal where water should not be. Intermediate signal is degeneration.
- A meniscal tear needs the signal to reach the surface, on two or more images.
- Intermediate signal that vanishes on T2 near 55 degrees is magic angle, not disease.

</div>

## References

1. Johnson PW, Collins MS, Wenger DE. Diagnostic utility of T1-weighted MRI characteristics in evaluation of osteomyelitis of the foot. *AJR Am J Roentgenol.* 2009;192(1):96–100. PMID [19098186](https://pubmed.ncbi.nlm.nih.gov/19098186/).
2. Zajick DC Jr, Morrison WB, Schweitzer ME, Parellada JA, Carrino JA. Benign and malignant processes: normal values and differentiation with chemical shift MR imaging in vertebral marrow. *Radiology.* 2005;237(2):590–596. [doi:10.1148/radiol.2372040990](https://doi.org/10.1148/radiol.2372040990). PMID [16244268](https://pubmed.ncbi.nlm.nih.gov/16244268/).
3. De Smet AA, Tuite MJ. Use of the "two-slice-touch" rule for the MRI diagnosis of meniscal tears. *AJR Am J Roentgenol.* 2006;187(4):911–914. PMID [16985134](https://pubmed.ncbi.nlm.nih.gov/16985134/).
4. Erickson SJ, Cox IH, Hyde JS, Carrera GF, Strandt JA, Estkowski LD. Effect of tendon orientation on MR imaging signal intensity: a manifestation of the "magic angle" phenomenon. *Radiology.* 1991;181(2):389–392. [doi:10.1148/radiology.181.2.1924777](https://doi.org/10.1148/radiology.181.2.1924777).
5. Chang CY, Garner HW, Ahlawat S, et al. Society of Skeletal Radiology white paper. Guidelines for the diagnostic management of incidental solitary bone lesions on CT and MRI in adults: bone reporting and data system (Bone-RADS). *Skeletal Radiol.* 2022;51(9):1743–1764. [doi:10.1007/s00256-022-04022-8](https://doi.org/10.1007/s00256-022-04022-8).
