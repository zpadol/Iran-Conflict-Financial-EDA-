import numpy as np
import streamlit as st
from datetime import timedelta
from visualization import*
from proj_func import *

with st.sidebar:
    st.subheader("🌍 Translate descriptions / Przetłumacz opisy", divider="gray")
    translate = st.toggle("Click to translate")
    st.subheader("🗓️Choose date to analyze:", divider="gray")
    start = st.date_input("Start date", pd.to_datetime("2026-02-24"))
    end = st.date_input("End date", pd.to_datetime("2026-03-31"))
if translate:
    st.title("📈EIMI & Ropa w czasach konfliktu w Iranie")
else:
    st.title("📈EIMI & Oil during conflict in Iran")

st.subheader(f"From {start} to {end}", divider="gray")

# Przygotowanie Tickerów
assets1 = [
    ("EIMI.L", "EIMI_Price"),
    ("CL=F", "Oil_Price")
]
assets2 = [
    ("EIMI.L", "EIMI_Price"),
    ("CL=F", "Oil_Price"),
    ("GC=F", "Gold_Price"),
    ("DX-Y.NYB", "USD_Price")
]
# wczytanie, czysczenie, laczenie
data_merged = get_merged_assets(assets1, start, end)

# wczytanie, czyszczenie, normalizacja, laczenie + ekstrema
pct_full_merged, extremes_all = get_all_data_with_extremes(assets2, start, end) # oil,eimi,gold,USD
pct_merged = pct_full_merged[[
    "EIMI_Price", "EIMI_Price_pct_change",
    "Oil_Price", "Oil_Price_pct_change"
]]

# przygotowanie danych, obliczanie zmiany calkowitej
total_change_eimi = get_total_change("EIMI.L", "EIMI_Price", start, end)
total_change_oil = get_total_change("CL=F", "Oil_Price", start, end)

tab1,tab2,tab3, tab4, tab5 = st.tabs(["General", "Volatility","Correlation", "Heatmap", "ROI"])

# przygtowanie danych, obliczanie modelu regresji, wyznaczenie statystyk
lm = get_regression_analysis_report(
    assets1, start, end, "Oil_Price", "EIMI_Price"
)
slope = round(lm['slope'],3)
r_sq = round(lm['rvalue'] ** 2,3)
p_val = round(lm['pvalue'],3)


with tab1:
    if translate:
        st.markdown("""
            ### Opis Analizy (PL)
            Niniejsze opracowanie skupia się na dynamice zmian cen ropy naftowej oraz wyników funduszu ETF na rynki wschodzące (EIMI - obejmującego m.in. Chiny, Indie czy Brazylię) w krytycznym momencie napięć geopolitycznych. Badanie koncentruje się na okresie eskalacji działań zbrojnych w Iranie, rozpoczynając się na kilka dni przed pierwszymi uderzeniami USA i Izraela, co pozwala na precyzyjne zaobserwowanie reakcji globalnego kapitału na nadchodzący kryzys. Dashboard oferuje pełną interaktywność - za pomocą paska bocznego można swobodnie modyfikować zakres dat do własnych analiz oraz przełączać język opisów między polskim a angielskim.
            """)
    else:
        st.markdown("""
            ### Analysis Description (EN)
            This analysis examines the price fluctuations of crude oil and the performance of the Emerging Markets ETF (EIMI – including markets such as China, India, and Brazil) during a period of intense geopolitical instability. The study focuses on the escalation of the 2026 conflict in Iran, beginning just days before the initial US and Israeli military strikes to capture the market's immediate response to the crisis. The dashboard is fully interactive, allowing users to adjust the date range for custom analysis and toggle the descriptions between Polish and English via the sidebar.
            """)

    col1,col2 = st.columns(2)
    with col1:
        if translate:
            st.subheader("Przegląd danych:")
            st.markdown("""
                        Poniższa tabela oraz wykresy prezentują surowe dane cenowe (USD) dla ropy naftowej oraz indeksu rynków wschodzących (EIMI). Kluczowym punktem odniesienia jest **28 lutego 2026 r.** (oznaczony czerwoną, przerywaną linią), kiedy to nastąpiła eskalacja konfliktu i atak na Iran.
                        W tym konkretnym punkcie zwrotnym obserwujemy wyraźną dywergencję:             
                        * **Ropa naftowa**: Gwałtowny wzrost cen wynikający z obaw o ciągłość dostaw z regionu Bliskiego Wschodu.                
                        * **EIMI**: Znaczący spadek wartości, będący reakcją na wzrost kosztów energii oraz ogólny wzrost niepewności na rynkach rozwijających się.
                        """)
        else :
            st.subheader("Data overview:")
            st.markdown("""
                        The table and charts below present the raw price data (USD) for crude oil and the Emerging Markets Index (EIMI). A critical reference point is **February 28, 2026** (marked with a red dashed line), representing the escalation of the conflict and the strikes on Iran.
                        At this specific turning point, we observe a clear market divergence:
                        * **Crude Oil**: A sharp price spike driven by supply chain concerns in the Middle East.
                        * **EIMI**: A significant decline in value, triggered by rising energy costs and a general "risk-off" sentiment across developing economies.
                        """)
    with col2:
        st.dataframe(data_merged)
    p1 = line_chart_eimi(data_merged)
    st.plotly_chart(p1)
    p2 = line_chart_oil(data_merged)
    st.plotly_chart(p2)

with tab2:
    if translate:
        st.markdown("""
        ### Analiza zmienności (PL)
       W niniejszej sekcji przedstawiono zestawienie zmian wartości wybranych aktywów w czasie. Dokonano porównania całkowitej, procentowej zmiany oraz analizy dziennych fluktuacji procentowych. Pozwala to na zidentyfikowanie momentów szczytowej niepewności rynkowej oraz dni, w których reakcja na wydarzenia geopolityczne była najbardziej znacząca.""")

    else:
        st.markdown("""
        ### Volatility analysis (EN)
        This section presents a comparison of the value fluctuations of the selected assets over time. Compared total percentage changes and analysed daily price fluctuations, allowing for the identification of periods of peak market uncertainty and days with the most significant reactions to geopolitical events.         """)

    v1 = data_merged["EIMI_Price"].iloc[-1]
    v2 = data_merged["Oil_Price"].iloc[-1]
    v1 = np.round(v1,2)
    v2 = np.round(v2,2)

    p3 = normalized(data_merged)
    st.plotly_chart(p3)

    if translate:
        st.subheader("📊 Dziene zmiany (Procentowe) (PL)")
    else:
        st.subheader("📊 Daily changes (Percentage Change) (EN)")

    styled_pct = pct_merged.style.map(color_delta, subset=["EIMI_Price_pct_change", "Oil_Price_pct_change"])
    styled_pct = styled_pct.format("{:.2f}%", subset=["EIMI_Price_pct_change", "Oil_Price_pct_change"])

    st.dataframe(styled_pct)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("EIMI Total Change", f"{v1} USD", f"{total_change_eimi} %")

    with col2:
        st.metric("Oil Total Change %", f"{v2} USD", f"{total_change_oil} %")

    col1, col2 = st.columns(2)
    with col1:
        ext_eimi = extremes_all["EIMI_Price"]
        st.metric(
            label=f"Max change EIMI ({ext_eimi['max_date']})",
            value=f"{ext_eimi['max_value']:.2f}%"
        )
        st.metric(
            label=f"Max Negative change EIMI ({ext_eimi['min_date']})",
            value=f"{ext_eimi['min_value']:.2f}%"
        )
    with col2:
        ext_oil = extremes_all["Oil_Price"]
        st.metric(
            label=f"Max change Oil ({ext_oil['max_date']})",
            value=f"{ext_oil['max_value']:.2f}%"
        )
        st.metric(
            label=f"Max Negative change Oil ({ext_oil['min_date']})",
            value=f"{ext_oil['min_value']:.2f}%"
        )

    if translate:
        st.markdown(f"""
        Powyższy wykres ilustruje gwałtowną aprecjację cen ropy naftowej przy jednoczesnej, wyraźnej deprecjacji indeksu EIMI. Skumulowana zmiana w badanym okresie wyniosła odpowiednio {total_change_oil}% dla ropy oraz {total_change_eimi}% dla EIMI. Biorąc pod uwagę krótki horyzont czasowy (niecały miesiąc), skala tych przesunięć jest wyjątkowo duża.
        
        Kluczowe obserwacje z tabeli zmian procentowych:
       * Przeciwstawne zwroty: W większości sesji znaki dziennych stóp zwrotu są odwrotne – wzrostom jednego aktywa towarzyszą spadki drugiego.
       * Ekstrema (10 marca): Najlepszy dowód ujemnej korelacji odnotowano 10 marca. Tego dnia indeks EIMI osiągnął swój maksymalny dzienny wzrost (+3,21%), co precyzyjnie zbiegło się w czasie z najgłębszym dziennym spadkiem cen ropy (-11,94%).
      
      **Analiza zdarzeniowa**
      
      6 marca 2026:      
      Największy wzrost ceny ropy (12%) zbiegł się w czasie z rozpoczęciem przez Izrael operacji „Roaring Lion” wymierzonej bezpośrednio w Teheran. Kluczowym czynnikiem zapalnym było zniszczenie strategicznego centrum dowodzenia w stolicy Iranu oraz zmasowane ataki na ponad 400 celów militarnych, co wywołało u inwestorów obawy o całkowite wstrzymanie eksportu surowca z regionu Zatoki Perskiej.
     Dodatkowo, tego samego dnia Donald Trump zażądał od Iranu „unconditional surrender” (bezwarunkowej kapitulacji). Ta radykalna retoryka polityczna odcięła drogę do negocjacji, stając się kluczowym katalizatorem rekordowego wzrostu cen ropy.
       """)

    else :
        st.markdown(f"""
        The chart above illustrates a rapid surge in oil prices alongside a noticeable and significant decline in the EIMI index. The total changes recorded were {total_change_oil}% for oil and {total_change_eimi}% for EIMI, respectively. Given the short analysis window—just over a month—the magnitude of these shifts is extraordinary.
        
        Key observations from the percentage change table:
        * Inverse Returns: In the majority of sessions, the daily returns show opposite signs—gains in one asset are typically accompanied by losses in the other.
       * Daily Extremes (March 10th): The strongest evidence of this negative correlation occurred on March 10th. On this day, the EIMI index reached its maximum daily gain (+3.21%), precisely coinciding with the sharpest daily decline in oil prices (-11.94%).
        
        **Event Study** 
        
        March 6, 2026:     
        The highest surge in oil prices during the analyzed period (12%) coincided with the launch of Israel's "Roaring Lion" operation, directly targeting Tehran. Key triggers included the destruction of a strategic command center in the Iranian capital and massive strikes on over 400 military targets. This sparked widespread investor panic regarding a potential total halt of oil exports from the Persian Gulf.
        Furthermore, on this same day, Donald Trump demanded Iran's "unconditional surrender". This radical political rhetoric effectively closed the door to diplomatic negotiations, serving as a primary catalyst for the record percentage increase in oil prices.
        """)
with (tab3):
    if translate:
        st.subheader("🖇️Analiza korelacji (PL)")
        st.markdown("""
               W niniejszej sekcji przeprowadzono badanie zależności pomiędzy wybranymi zmiennymi. Wyznaczono wartość korelacji Pearsona oraz przedstawiono wzajemny wpływ zmian cen aktywów za pomocą wykresu rozrzutu z nałożoną linią regresji. Analizie poddano kluczowe parametry statystyczne modelu, takie jak współczynnik determinacji ($R^2$) oraz istotność statystyczną ($p$-value). Pozwoliło to na ocenę siły wpływu jednej zmiennej na drugą oraz zweryfikowanie wiarygodności otrzymanego modelu.
               """)
    else:
        st.subheader("🖇️Correlation analysis (EN)")
        st.markdown("""
               This section examines the relationship between the selected variables. The Pearson correlation coefficient was calculated, and the mutual impact of asset price changes was visualized using a scatter plot with an integrated regression line. Key statistical parameters of the model, including the coefficient of determination ($R^2$) and statistical significance ($p$-value), were analyzed. This allowed for an assessment of the impact strength of one variable on another and a verification of the model's reliability.
               """)
    matrix = pct_merged.corr()
    corr_value = matrix.loc["EIMI_Price_pct_change", "Oil_Price_pct_change"]

    st.metric(label="Pearson Correlation (r)", value=f"{corr_value:.2f}")

    sc = scatter_chart(pct_merged)
    st.plotly_chart(sc)

    if translate:
        st.markdown(f"""
            Współczynnik korelacji Pearsona wynosi {corr_value:.2f}, co wskazuje na umiarkowaną ujemną korelację. Wynik ten potwierdza tendencję do **przeciwstawnego zachowania cen** obu aktywów: wzrostowi cen ropy naftowej zazwyczaj towarzyszy spadek wartości indeksu EIMI. Zależność tę obrazuje linia regresji na wykresie rozrzutu.
            Potencjalne przyczyny ujemnej korelacji:
            * **Koszty produkcji i importu**: Wiele gospodarek wchodzących w skład indeksu EIMI (np. Indie, Chiny, Turcja) to potężni importerzy netto ropy. Wzrost cen surowca bezpośrednio uderza w rentowność ich sektorów produkcyjnych (np. przemysł chemiczny, odzieżowy jak Inditex/H&M korzystający z poliestrów, czy transportowy).
            * **Sentyment rynkowy (Risk-Off)**: Eskalacja konfliktu zbrojnego wywołuje panikę i ucieczkę kapitału do bezpieczniejszych aktywów (Safe Havens), co skutkuje wyprzedażą ryzykownych akcji rynków wschodzących przy jednoczesnym wzroście cen ropy spowodowanym obawami o podaż. 
            
            Dlaczego korelacja nie jest wyższa?
            W indeksie EIMI znajdują się również państwa będące znaczącymi eksporterami surowców energetycznych (np. Arabia Saudyjska, Brazylia, Meksyk, Zjednoczone Emiraty Arabskie). Kraje te zyskują na droższej ropie, co częściowo równoważy spadki całego indeksu. Należy również pamiętać, że odnotowana korelacja może nie wynikać z bezpośredniego wpływu ropy na EIMI, lecz być wspólnym skutkiem zewnętrznym trwającej wojny.""")
    else:
        st.markdown(f"""
               The Pearson correlation coefficient is {corr_value:.2f}, indicating a moderate negative correlation. This result confirms an **inverse relationship**: rising crude oil prices are generally accompanied by a decline in the EIMI index. This trend is further illustrated by the regression line on the scatter plot.
                
                Potential drivers of the negative correlation:
                * **Production and Import Costs**: Many economies within the EIMI index (e.g., India, China, Turkey) are major net oil importers. Rising energy prices directly impact the profitability of their manufacturing sectors (e.g., chemical industries, textile production relying on synthetics, and logistics).
                * **Market Sentiment (Risk-Off)**: Geopolitical escalation often triggers a "flight to quality," where investors sell off risky emerging market equities in favor of safer assets, while oil prices spike due to supply chain disruptions.
                
                Why is the correlation not stronger?
                The EIMI index also includes countries that are significant energy exporters (e.g., Saudi Arabia, Brazil, Mexico, UAE). These nations benefit from higher oil prices, which partially offsets the broader index's decline. It is also important to consider that this correlation might not imply direct causation, but rather represent a synchronized market reaction to the ongoing conflict.
                """)

    if translate:
        st.subheader("🔎Model linii regresji (PL)")

    else:
        st.subheader("️🔎Regression model (EN)")

    c1,c2,c3 = st.columns(3)
    with c1:
        st.metric("Slope", slope )

    with c2:
        st.metric("R-Squared", r_sq)

    with c3:
        st.metric("p-value",p_val)

    if translate:
        st.markdown(f"""
        1. **Wrażliwość (Slope: {slope})**
        Współczynnik kierunkowy potwierdza ujemną zależność: statystycznie wzrost ceny ropy o 1% przekłada się na spadek wartości indeksu EIMI o ok. {-slope}%. Świadczy to o tym, że rynki wschodzące są wrażliwe na szoki energetyczne, choć reakcja nie jest gwałtownie proporcjonalna.
        2. **Siła wyjaśniająca ($R^2$: {r_sq*100:.0f}%)**
        Wartość współczynnika determinacji wskazuje, że ropa naftowa wyjaśnia {r_sq*100:.0f}% zmienności indeksu EIMI w badanym okresie. W analizie rynków finansowych, gdzie na ceny wpływają tysiące zmiennych (stopy procentowe, inflacja, polityka Chin), wynik ok. 40% dla pojedynczego surowca jest uznawany za znaczący. Potwierdza to, że w czasie konfliktu w Iranie ropa stała się jednym z głównych (choć oczywiście nie jedynym) motorów napędowych zmian na giełdach.
        3. **Wiarygodność (p-value: {p_val})**
        Otrzymany wynik $p < 0.01$ pozwala z wysoką pewnością odrzucić hipotezę o przypadkowości tych powiązań. Zależność jest istotna statystycznie, co oznacza, że zaobserwowany trend spadkowy EIMI przy rosnącej ropie ma swoje głębokie uzasadnienie w danych, a nie jest jedynie dziełem przypadku.
        """)
    else:
        st.markdown(f"""
        1. **Sensitivity (Slope: {slope})**
        The slope coefficient confirms a negative correlation: statistically, a 1% increase in oil prices translates to an approx. {-slope}% decrease in the EIMI index value. This indicates that emerging markets are sensitive to energy shocks, although the reaction is not strictly proportional.
        2. **Explanatory Power ($R^2$: {r_sq*100:.0f}%)**
        The coefficient of determination indicates that crude oil explains {r_sq*100:.0f}% of the EIMI index volatility during the analyzed period. In financial market analysis - where prices are influenced by thousands of variables (interest rates, inflation, geopolitical shifts) - a result of around 40% for a single commodity is considered highly significant. This confirms that during the Iran conflict, oil became one of the primary (though not the only) drivers of stock market movements.
        3. **Reliability (p-value: {p_val})**
        The result of $p < 0.01$ allows for the rejection of the null hypothesis regarding the randomness of these associations with high confidence. The relationship is statistically significant, meaning the observed downward trend in EIMI alongside rising oil prices is deeply rooted in the data and is not merely a coincidence.
        """)

with tab4:
    if translate:
        st.subheader("Korelacja ze złotem i dolarem - Mapa Cieplna (PL)")
        st.markdown("""
        W tej sekcji, za pomocą mapy cieplnej, zbadano wzajemne powiązania między czterema aktywami: indeksem rynków wschodzących (EIMI), ropą naftową (Oil), oraz dodatkowo, złotem (Gold) oraz indeksem dolara amerykańskiego (USD Index). Celem badania jest identyfikacja kierunków przepływu kapitału w obliczu konfliktu w Iranie.
                """)
    else:
        st.subheader("️Correlation with gold and USD - Heatmap (EN)")
        st.markdown("""
       This section utilizes a heatmap to examine the interdependencies between four key assets: the Emerging Markets Index (EIMI), Crude Oil, and additionally, Gold, and the US Dollar Index. The objective is to identify capital flight patterns triggered by the Iranian conflict. 
                """)
    st.pyplot(heatmap(pct_full_merged))
    if translate:
        st.markdown("""
        Mapa ujawnia kluczowe mechanizmy przepływu kapitału w warunkach wojennych:
        * Ucieczka do Dolara: Ujemna korelacja między EIMI a USD potwierdza odwrót od ryzykownych akcji na rzecz bezpiecznej waluty (Safe Haven).
        * Zależność EIMI – Złoto (ok. 0,5): Dodatni współczynnik wskazuje na zbliżony kierunek zmian. Może to sugerować, że w szczytowej fazie paniki złoto nie zadziałało jako tarcza.
        * Ropa i Dolar (ok. 0,6): Wyniki zmieniają się zgodnie - potwierdza to ucieczkę do Dolara (stabilnego aktywa). Inwestorzy w czasach paniki kupują ropę i dolara.
                """)
    else:
        st.markdown("""
        The map reveals key capital flow mechanisms under wartime conditions:
        * Flight to the Dollar: The negative correlation between EIMI and USD confirms a shift away from risky equities toward a safe-haven currency (Safe Haven).
        * EIMI – Gold Relationship (approx. 0.5): The positive coefficient indicates a similar direction of change. This may suggest that during the peak phase of the panic, gold did not act as a hedge.
        * Oil and the Dollar (approx. 0.6): The results move in sync – this confirms the flight to the Dollar (a stable asset). In times of panic, investors buy both oil and the dollar.
                    """)
with tab5:
    t_roi_title = "💰 Hipotetyczny zwrot z inwestycji" if translate else "💰 Hypothetical ROI"

    st.subheader(t_roi_title)
    if translate:
        st.markdown("""
        Dla odmiany, ta sekcja zawiera narzędzie do **"backtesting"** (kalkulator wsteczny), które umożliwia obliczenie teoretycznego zwrotu z inwestycji o określonej wartości w wybrane aktywa. Narzędzie pozwala na zbadanie, jak kwota kapitału zmieniałaby się w dowolnie zdefiniowanym przedziale czasowym, co ułatwia analizę wpływu momentu wejścia na rynek (tzw. market timing) na ostateczny wynik finansowy.
                   """)
    else:
        st.markdown("""
        Conversly, this feature offers a **backtesting tool (retrospective calculator)** designed to calculate theoretical investment returns for a specific amount in selected assets. The tool allows users to examine how capital would have fluctuated over a custom-defined timeframe, facilitating an analysis of how investment timing affects the final financial outcome.
                   """)

    col_d1, col_d2 = st.columns(2)
    selected_date = st.slider(
        "Select a date range",
        min_value=start,
        max_value=end,
        value=(start, end),
        step=timedelta(days=1),
    )
    bdate, sdate = selected_date

    amount = st.number_input("Investment amount (USD):", value=100, min_value=1)
    chosen_df = pct_merged.loc[bdate:sdate]

    tgl = st.toggle("EIMI/Oil")
    if tgl:
        final_value, profit, profit_pct, icon = get_roi_report(chosen_df, "Oil_Price", amount )
        st.metric(
            label=f"Oil Investment Result  {icon}️",
            value=f"{final_value:.2f} USD",
            delta=f"{profit:.2f} USD ({profit_pct:.1f}%)",
            delta_color="normal"
        )
    else :
        final_value, profit, profit_pct, icon = get_roi_report(chosen_df, "EIMI_Price", amount )
        st.metric(
            label = f"EIMI Investment Result {icon}",
            value=f"{final_value:.2f} USD",
            delta=f"{profit:.2f} USD ({profit_pct:.1f}%)",
            delta_color="normal"
        )