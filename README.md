# SAIL-to-CGEN---Coding-Challenge
# YAML → S-Expression Converter

This tool converts structured data (YAML) into a **Lisp-style S-expression** format.  
It demonstrates the concept behind the **SAIL → CGEN** pipeline, where structured ISA specifications are transformed into CGEN's S-expression DSL for GCC.

---

## ✅ Why This Matters
The **SAIL → CGEN** flow converts high-level ISA specifications into CGEN DSL (which uses S-expressions).  
This project demonstrates **semantic-preserving structured → Lisp transformation**, a critical concept for automating compiler support for custom ISAs.

---

## ✅ Installation
Install dependencies:
```bash
pip install pyyaml
```

---

## ✅ Usage
Convert YAML to S-expressions:

```bash
python yaml_to_sexpr.py --input example.yaml --pretty
```

### Options:
- `--input, -i` : Path to YAML file.
- `--output, -o`: Optional output file.
- `--format, -f`: Force input format (`yaml`).
- `--pretty`: Pretty-print output with indentation.
- `--env`: Enable `${VAR}` environment variable substitution.

---

## ✅ Input Example
**example.yaml**
```yaml
receipt: "Oz-Ware Purchase Invoice"
date: 2012-08-06
customer:
  first_name: Dorothy
  family_name: Gale
items:
  - part_no: A4786
    descrip: Water Bucket (Filled)
    price: 1.47
    quantity: 4
  - part_no: E1628
    descrip: High Heeled "Ruby" Slippers
    size: 8
    price: 133.7
    quantity: 1
bill-to:
  street: |
    123 Tornado Alley
    Suite 16
  city: East Centerville
  state: KS
ship-to:
  street: |
    123 Tornado Alley
    Suite 16
  city: East Centerville
  state: KS
specialDelivery: >
  Follow the Yellow Brick Road to the Emerald City.
  Pay no attention to the man behind the curtain.
```

---

## ✅ Output Example
```lisp
((yaml:receipt "Oz-Ware Purchase Invoice")
 (yaml:date (make-date 2012 08 06))
 (yaml:customer
   (yaml:first_name 'Dorothy)
   (yaml:family_name 'Gale))
 (yaml:items
   ((yaml:item
      (yaml:part_no 'A4786)
      (yaml:descrip "Water Bucket (Filled)")
      (yaml:price 1.47)
      (yaml:quantity 4))
    (yaml:item
      (yaml:part_no 'E1628)
      (yaml:descrip "High Heeled \"Ruby\" Slippers")
      (yaml:size 8)
      (yaml:price 133.7)
      (yaml:quantity 1))))
 (yaml:bill-to
   (yaml:street "123 Tornado Alley\nSuite 16\n")
   (yaml:city "East Centerville")
   (yaml:state 'KS))
 (yaml:ship-to
   (yaml:street "123 Tornado Alley\nSuite 16\n")
   (yaml:city "East Centerville")
   (yaml:state 'KS))
 (yaml:specialDelivery
   "Follow the Yellow Brick Road to the Emerald City. Pay no attention to the man behind the curtain.\n"))
```
