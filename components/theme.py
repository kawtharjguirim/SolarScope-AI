"""Charte visuelle SolarScope AI (prototype HTML) : CSS, en-têtes, cartes, états vides."""
import streamlit as st

COLORS = {
    "bg": "#07111F", "sidebar": "#091625", "card": "#0D1B2D", "card2": "#10233A",
    "cyan": "#45D6D0", "violet": "#8B7CFF", "gold": "#FFC66D", "green": "#63D9A4",
    "text": "#EDF5FF", "muted": "#91A6BF", "red": "#FF7F8B", "grey": "#6B7A90",
}

CSS = """
<style>
@keyframes ss-drift {0%{transform:translate(0,0) scale(1)}50%{transform:translate(-2%,3%) scale(1.06)}100%{transform:translate(0,0) scale(1)}}
@keyframes ss-fade {from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.ss-bg{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden}
.ss-bg:before{content:"";position:absolute;width:70vw;height:70vw;right:-15vw;top:-25vw;border-radius:50%;
  background:radial-gradient(circle,#8B7CFF33,transparent 65%);animation:ss-drift 18s ease-in-out infinite}
.ss-bg:after{content:"";position:absolute;width:60vw;height:60vw;left:-20vw;bottom:-25vw;border-radius:50%;
  background:radial-gradient(circle,#45D6D033,transparent 65%);animation:ss-drift 22s ease-in-out infinite reverse}
.ss-title{font-size:3.2rem;font-weight:800;line-height:1.05;letter-spacing:-2px;margin:.3rem 0 .8rem;animation:ss-fade .8s ease both}
.ss-grad{background:linear-gradient(90deg,#45D6D0,#A99BFF 60%,#FFC66D);-webkit-background-clip:text;background-clip:text;color:transparent}
.ss-eyebrow{display:inline-block;color:#45D6D0;background:#45d6d012;border:1px solid #45d6d033;border-radius:30px;
  padding:6px 12px;font-size:.72rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase}
.ss-lead{color:#91A6BF;font-size:1.05rem;line-height:1.75;max-width:44rem}
.ss-brand{display:flex;align-items:center;gap:12px;font-weight:800;font-size:1.1rem;letter-spacing:-.4px}
.ss-logo{width:38px;height:38px;border-radius:13px;background:linear-gradient(135deg,#45D6D0,#8B7CFF);
  display:grid;place-items:center;color:#07111F;font-size:21px;box-shadow:0 8px 30px #45d6d033}
.ss-brand small{display:block;color:#91A6BF;font-size:9px;letter-spacing:2px;font-weight:700}
div[data-testid="stVerticalBlockBorderWrapper"]{background:linear-gradient(145deg,#11243a,#0c1a2b);
  border-radius:18px!important;border-color:#a4bedc24!important;transition:transform .2s,border-color .2s,box-shadow .2s;
  animation:ss-fade .5s ease both}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{transform:translateY(-2px);border-color:#45d6d066!important;
  box-shadow:0 12px 36px #0008}
div[data-testid="stMetric"]{background:transparent}
div[data-testid="stMetricValue"]{font-weight:800;letter-spacing:-.5px}
.ss-pill{display:inline-block;padding:4px 9px;border-radius:20px;font-size:.7rem;color:#63D9A4;background:#63d9a415}
.ss-pill.warn{color:#FFC66D;background:#ffc66d15}
.ss-pill.off{color:#91A6BF;background:#ffffff0d}
.ss-quant{display:flex;gap:8px;margin-top:.6rem}
.ss-q{flex:1;padding:12px;border-radius:12px;background:#ffffff08;border-top:2px solid #8B7CFF}
.ss-q.mid{border-top-color:#45D6D0}.ss-q.hi{border-top-color:#FFC66D}
.ss-q small{display:block;color:#91A6BF;font-size:.68rem;letter-spacing:.5px}
.ss-q b{display:block;font-size:1.2rem;margin-top:5px}
.ss-note{color:#91A6BF;font-size:.8rem;line-height:1.6}
.ss-empty{padding:18px;border:1px dashed #a4bedc40;border-radius:14px;color:#91A6BF;text-align:center}
.ss-foot{color:#91A6BF;font-size:.78rem;text-align:center;padding:1.5rem 0;border-top:1px solid #a4bedc22;margin-top:2rem}
</style>
"""


def inject():
    """Injecte la charte et le fond animé (à appeler une fois par page)."""
    st.html(CSS + "<div class='ss-bg'></div>")


def header(title, desc, eyebrow=None):
    if eyebrow:
        st.markdown(f"<span class='ss-eyebrow'>{eyebrow}</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='ss-title ss-grad' style='font-size:2rem'>{title}</div>",
                unsafe_allow_html=True)
    st.caption(desc)


def brand(subtitle="SOLAR INTELLIGENCE PLATFORM"):
    st.markdown(
        f"<div class='ss-brand'><div class='ss-logo'>☼</div>"
        f"<span>SolarScope AI<small>{subtitle}</small></span></div>",
        unsafe_allow_html=True,
    )


def kpi(label, value, help_text=None, delta=None, delta_color="off"):
    with st.container(border=True):
        st.metric(label, value, delta=delta, delta_color=delta_color, help=help_text)


def empty_state(message="Résultats expérimentaux non disponibles pour le moment."):
    st.markdown(f"<div class='ss-empty'>{message}</div>", unsafe_allow_html=True)


def quantile_boxes(q10, q50, q90, unit):
    st.markdown(
        f"<div class='ss-quant'>"
        f"<div class='ss-q'><small>Q10 · BAS</small><b>{q10:.2f}</b></div>"
        f"<div class='ss-q mid'><small>Q50 · MÉDIAN</small><b>{q50:.2f}</b></div>"
        f"<div class='ss-q hi'><small>Q90 · HAUT</small><b>{q90:.2f}</b></div>"
        f"</div><div class='ss-note'>{unit}</div>",
        unsafe_allow_html=True,
    )


def pill(text, kind=""):
    return f"<span class='ss-pill {kind}'>{text}</span>"
