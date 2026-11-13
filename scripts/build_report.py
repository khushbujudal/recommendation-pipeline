from pathlib import Path
import html, json, re
import reportlab
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
font_dir=Path(reportlab.__file__).resolve().parent/'fonts'
pdfmetrics.registerFont(TTFont('DejaVu', str(font_dir/'Vera.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuBold', str(font_dir/'VeraBd.ttf')))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold',italic='DejaVu',boldItalic='DejaVuBold')
R=Path(__file__).resolve().parents[1]
details=json.loads((R/'submission_details.json').read_text())
report=R/'reports'
run=json.loads((report/'workflow_run.json').read_text())
validation=json.loads((report/'validation.json').read_text())
results=pd.read_csv(report/'evaluation.csv')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='DejaVu',fontSize=9.5,leading=13,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallCustom',fontName='DejaVu',fontSize=9,leading=12,spaceAfter=6))
styles['Title'].fontName='DejaVuBold'
styles['Heading1'].fontName='DejaVuBold'
styles['Title'].textColor=colors.black
styles['Title'].fontSize=21
styles['Title'].leading=28
styles['Title'].spaceAfter=12
styles['Heading1'].textColor=colors.black
styles['Heading1'].fontSize=15
styles['Heading1'].leading=19
styles['Heading1'].spaceBefore=12
styles['Heading1'].spaceAfter=7
story=[]
markdown=['# Movie Recommendation Data Pipeline', '', 'Data Management for Machine Learning | Assignment 2', '']
for key,label in [('student_name','Student name'),('roll_number','Roll number'),('email','Email'),('repository_url','Repository URL')]:
    markdown.extend([label+': '+details.get(key,''),''])
def plain(s): return html.unescape(re.sub(r'<[^>]+>', '',s))
def p(s):
    story.append(Paragraph(s,styles['BodyCustom']))
    markdown.extend([plain(s),''])
def h(s):
    story.append(Paragraph(s,styles['Heading1']))
    markdown.extend(['## '+plain(s),''])
class IdentityFields(Flowable):
    def __init__(self):
        super().__init__()
        self.width=504
        self.height=88
    def draw(self):
        c=self.canv
        for row,(name,label) in enumerate([('student_name','Student name'),('roll_number','Roll number'),('email','Email'),('repository_url','Repository URL')]):
            y=70-row*21
            c.setFont('DejaVu',9)
            c.drawString(0,y+4,label)
            c.acroForm.textfield(name=name,tooltip=label,value=details.get(name,''),x=100,y=y,width=400,height=18,
                relative=True,fontName='Helvetica',fontSize=9,borderStyle='underlined',borderWidth=.5,
                borderColor=colors.HexColor('#b5bec8'),fillColor=colors.white,textColor=colors.black,
                forceBorder=True,maxlen=240)

def table(rows,widths):
    markdown.append('| '+' | '.join(plain(str(x)) for x in rows[0])+' |')
    markdown.append('| '+' | '.join('---' for _ in rows[0])+' |')
    for row in rows[1:]: markdown.append('| '+' | '.join(plain(str(x)) for x in row)+' |')
    markdown.append('')
    data=[[Paragraph(str(x),styles['SmallCustom']) for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4e9ef')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,9))
story.append(Paragraph('Movie Recommendation Data Pipeline',styles['Title']))
p('Data Management for Machine Learning | Assignment 2')
story.append(IdentityFields())
story.append(Spacer(1,7))
p('I implemented a reproducible pipeline from raw CSV ingestion through validation, time-based preparation, feature management, training, evaluation and automated orchestration. A content-based personalized recommender improves held-out relevance over a popularity baseline on a controlled synthetic movie dataset, while reducing genre diversity.')
h('Data and design decisions')
p('The seeded generator creates 180 users, 120 fictional movies across six categories and 6,480 distinct user-item interactions. Each user has one hidden preferred category; preferred-category ratings tend to be higher. Exposure also has a weaker shared item-popularity effect. Ratings are integers from 1 to 5 and timestamps fall in 2024. No personal data or external dataset is used. The hidden preference is excluded from model inputs.')
p('Synthetic data is permitted by the brief and keeps execution self-contained. Seven malformed rows and three duplicate rows are deliberately injected to demonstrate quality controls. The generator writes three CSV files, which ingestion then reads. A fixed seed of 42 and pinned NumPy and Pandas versions make input generation and metrics repeatable.')
h('Validation and temporal preparation')
p('Every entity is checked for required fields, nulls, duplicates, numeric identifier types and valid keys. Interactions also require integer ratings in [1, 5], valid timestamps no later than the configured as-of date, and existing user and item references. Invalid records retain reason codes in an error dataset. Required invalid fields are rejected; derived aggregate defaults are handled separately.')
table([['Entity','Input','Accepted','Rejected']]+[[n,v['input'],v['accepted'],v['rejected']] for n,v in validation.items()],[162,110,110,110])
p(f'The global 80th-percentile timestamp cutoff is {run["cutoff"]}. Training contains {run["train_rows"]:,} interactions and test contains {run["test_rows"]:,}. Ties at the cutoff stay in training, so every test timestamp is strictly later. Formats are normalized before deriving user activity summaries, item popularity and a compressed user-item rating matrix with ID mappings.')
story.append(PageBreak())
h('Reusable feature management')
p('Features are computed solely from the training partition. Snapshot CSVs are reusable in training, evaluation and reloaded prediction. The experiment stores the category profiles alongside model artifacts. The full catalog, including definitions, grain, types, source and defaults, is provided as reports/feature_catalog.csv.')
table([['Entity','Features','Use and default'],['User','Activity count, average rating, last interaction, recency','Audit summaries; zero activity and training global mean for missing averages'],['User category','Mean of rating minus 3; preferred category','Personalized scores; unseen category affinities are zero'],['Item','Category, activity, average rating, positive count, normalized popularity','Model candidates and baseline; zero count for unobserved items'],['Interaction','Affinity = rating minus 3','Reusable training event feature; invalid source ratings rejected']],[85,205,202])
p('The shared user_profile function is used during scoring and reloaded prediction. A cold user has an all-zero profile, which falls back to popularity ranking. An item without training interactions can still receive a category-based score. This is a small file-based feature layer; it does not provide online serving, historical feature version queries or production concurrency controls.')
h('Models and experiment tracking')
p('<b>Popularity baseline.</b> Rank unseen catalog items by the count of training ratings at least 4. Divide by the maximum item positive count to normalize scores to [0, 1].')
p('<b>Personalized content model.</b> Compute the user\'s mean centered rating within each category. Score a candidate as 0.95 times its category affinity plus 0.05 times normalized popularity. Filter all items previously interacted with in training. Break score ties by ascending item ID. The fixed weight is configured in advance and is not tuned using test results.')
p('A custom local experiment tracker records run ID, parameters, all model metrics, Python and package versions, source and raw-data SHA256 hashes, model JSONs and the feature snapshot. Unique timestamp-and-UUID directories retain independent experiments without an external server. This meets the experiment tracking requirement with an inspectable alternative to MLflow, but offers no registry UI or automatic promotion.')
h('Evaluation definitions')
p('K is 10. Relevance means a held-out rating of at least 4 for an item unseen in training. Evaluation ranks against the entire registered catalog after seen-item filtering, without negative sampling. Precision, recall and NDCG are macro averages over users with at least one eligible relevant test item. Both models use exactly the same cohort.')
p('Precision is hits divided by 10; recall is hits divided by that user\'s eligible relevant set size. Binary NDCG discounts each hit by log2(rank + 1) and divides by ideal discounted gain. Coverage is distinct recommended items divided by 120. Diversity is mean pairwise category inequality within each list, averaged across users. Lists with fewer than two items have diversity zero. These rankers do not predict explicit ratings, so RMSE and MAE are not applicable.')
story.append(PageBreak())
h('Measured results and interpretation')
rows=[['Model','Precision at 10','Recall at 10','NDCG at 10','Coverage','Diversity']]
for _,r in results.iterrows():rows.append([r['model']]+[f'{r[c]:.4f}' for c in ['precision_at_k','recall_at_k','ndcg_at_k','coverage','diversity']])
table(rows,[95,80,80,80,78,79])
p('Both models were evaluated on 177 of the 180 users; three users had no eligible relevant test item. The personalized model increases precision from 0.0407 to 0.2548, recall from 0.1186 to 0.7545, and NDCG from 0.0722 to 0.5649. Catalog coverage rises from 19.17% to 100%. Coverage describes the union across users, not the breadth of each individual list.')
p('Mean diversity falls from 0.8202 to 0.2201 because category preferences concentrate recommendations. The result demonstrates a relevance-versus-diversity tradeoff. A diversity re-ranking layer could be evaluated later using a separate validation period. The personalized model is favored by the synthetic category-preference construction; this is not evidence of comparable improvement on real movie data.')
h('Orchestration and verification')
p('The workflow executes ingestion, validation, preparation, transformation, feature generation, training, evaluation and experiment tracking in dependency order. Each task logs status and runtime; a failure stops dependent tasks and records the exception. A weekly GitHub Actions schedule and manual trigger are included, plus a documented local cron alternative. Remote GitHub execution has not been verified.')
p('My macOS arm64 run used Python 3.14.10, NumPy 2.3.5 and pandas 2.3.3. Run 20261113T145310-bd72a082 completed all eight tasks. The supplied terminal screenshot shows four tests passing in 0.022 seconds: known-answer ranking metrics; invalid-data quarantine; temporal separation and training-only features; persisted model reload, seen-item filtering and cold-user fallback. Reference experiment outputs reproduce the same metrics. The dependency was updated from pandas 2.2.3 for Python 3.14 compatibility.')
h('Limitations and next steps')
p('The dataset is small and intentionally stationary, with one category per item, no delayed arrivals, no real exposure bias correction and no item availability timestamps. All registered items are assumed available before the cutoff. Evaluation excludes users without positive test items and does not measure online behavior, uncertainty intervals or robustness across seeds. Synthetic users do not demonstrate generalization to real users.')
p('Operational limits include sequential single-process execution, no automatic retry or partial-stage resume, file-based storage and a dense interaction matrix that will not scale to large catalogs. The next useful extensions are a real dataset, rolling temporal validation, richer content features, sparse storage and a managed orchestrator. The pipeline demonstrates the complete data management lifecycle while keeping data lineage, feature definitions, model comparison and execution evidence inspectable.')
def footer(c,d):
 c.setFont('DejaVu',9); c.setFillColor(colors.HexColor('#555555'));c.drawString(54,30,'Data Management for Machine Learning | Assignment 2');c.drawRightString(558,30,str(d.page))
SimpleDocTemplate(str(report/'final_report.pdf'),title='Movie Recommendation Data Pipeline',author=details.get('student_name',''),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=43,bottomMargin=48).build(story,onFirstPage=footer,onLaterPages=footer)

(report/'final_report.md').write_text('\n'.join(markdown)+'\n')
print('Report written to', report/'final_report.pdf')

# Embed the document font in populated form appearances for consistent PDF rendering.
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, DictionaryObject, ArrayObject, NumberObject, DecodedStreamObject
pdf_path=report/'final_report.pdf'
reader=PdfReader(pdf_path)
writer=PdfWriter()
writer.clone_document_from_reader(reader)
page=writer.pages[0]
fonts=page['/Resources']['/Font']
font_ref=next(ref for ref in fonts.values() if 'VeraSans-Roman' in str(ref.get_object().get('/BaseFont','')))
for annotation_ref in page.get('/Annots',[]):
    annotation=annotation_ref.get_object()
    if annotation.get('/Subtype')!='/Widget': continue
    value=str(annotation.get('/V',''))
    escaped=value.replace(chr(92),chr(92)*2).replace('(',chr(92)+'(').replace(')',chr(92)+')')
    stream=DecodedStreamObject()
    stream.set_data(('q BT /IdentityFont 9 Tf 0 0 0 rg 2 5 Td ('+escaped+') Tj ET Q').encode('ascii'))
    stream.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Form'),
        NameObject('/BBox'):ArrayObject([NumberObject(0),NumberObject(0),NumberObject(400),NumberObject(18)]),
        NameObject('/Resources'):DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/IdentityFont'):font_ref})})})
    annotation[NameObject('/AP')]=DictionaryObject({NameObject('/N'):writer._add_object(stream)})
with pdf_path.open('wb') as output: writer.write(output)
