import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import math
from geopy.distance import geodesic
import chardet
from scipy.spatial import cKDTree


# 1) Must be the FIRST Streamlit command
st.set_page_config(
    page_title="طريقك لإيجاد نِطاقك المفضّل في الرياض",
    layout="wide"
)


# 2) Custom CSS for Styling
st.markdown(
    """
    <style>
    /* Make sidebar background light */
    [data-testid="stSidebar"] {
        background-color: #F5F5F5;
    }
    /* Make sidebar scrollable if content is long */
    [data-testid="stSidebar"] > div:first-child {
        overflow-y: auto;
        height: 100%;
    }
    /* Adjust main content padding */
    .css-18e3th9 {
        padding: 2rem 4rem;
    }
    /* Headings color */
    h1, h2, h3, h4 {
        color: #2C3E50;
    }
    .stats-box {
        background-color: #f0e5d8; /* Beige color */
        padding: 15px;
        margin: 10px;
        border-radius: 5px;
        display: inline-block;
        width: 30%;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stats-icon {
        font-size: 2rem;
    }
    /* Button styles */
    .stButton>button {
        background-color: #8D6E63;
        color: white;
        font-size: 16px;
        padding: 10px 20px;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        width: 100%;
        margin-bottom: 10px;
    }
    .stButton>button:hover {
        background-color: #6D4C41;
    }
    
    /* Custom styling for search options in sidebar */
    .sidebar .stWrite {
        color: #5A3E36;  /* Brown color */
        font-size: 16px;
    }
    
    .sidebar .stButton button {
        color: #9C27B0; /* Purple color */
    }
    
    /* Sidebar section title color */
    .sidebar .stSidebarHeader h2 {
        color: #2C3E50; /* Darker color for better visibility */
    }
    
    /* Sidebar labels */
    .sidebar label {
        color: #2C3E50; /* Dark text for contrast */
    }

    /* Professional Style for Main Content */
    .main-content {
        background-color: #2C3E50;
        padding: 3rem;
        border-radius: 10px;
        color: #ffffff;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Heading Style */
    .main-content h1 {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Paragraph Style */
    .main-content p {
        font-size: 1.2rem;
        color: #bdc3c7;
        line-height: 1.6;
    }
    
    /* Sidebar input field styling */
    .stNumberInput, .stMultiselect, .stTextInput {
        background-color: #F5F5F5;
        color: #2C3E50;
        border-radius: 5px;
    }

    .stNumberInput input {
        color: #2C3E50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3) Title & Logo (Main Area)
st.markdown(
    "<div class='main-content'><h1>طريقك لإيجاد نطاقك المفضّل في الرياض!</h1></div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class='main-content'>
    <p style="font-size: 1.5rem; font-weight: bold;">مرحبًا بك في تطبيق <strong>نِطاق</strong>!</p>
    <p>نساعدك في استكشاف الرياض والعثور على النّـطاق المثالي الذي يناسبك، بناءً على المعالم والخدمات القريبة منك.</p>
    <p>حدّد خياراتك من القائمة اليسرى، ثم قم بتحديد موقعك على الخريطة أو تكبيرها لاختيار الموقع المفضل لديك. 
    بعد ذلك، اضغط على زر "<em>تأكيد الموقع</em>" في الأسفل لإكمال العملية.</p>
    <p>بعد تأكيد الموقع، سنقوم بالخطوات التالية:</p>
    <ul>
        <li>سنريك تحليل مدروس للنّطاق</li>
        <li>سنقترح عليك الشقق المتاحة للإيجار في نِطاقك</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)






# Function to detect encoding and load data
@st.cache_data
def load_places_data(path):
    with open(path, 'rb') as f:
        raw_data = f.read(10000)  # Read a sample of the file
        result = chardet.detect(raw_data)
        encoding_type = result['encoding']
    return pd.read_csv(path, encoding=encoding_type)



# Load data
file_path = "Riyadh_data.csv"
try:
    places_df = load_places_data(file_path)
    places_df_v2 = load_places_data(file_path)
    st.success("تم تحميل بيانات الخدمات بنجاح!")
except Exception as e:
    st.error(f"حدث خطأ أثناء تحميل الملف: {e}")
    st.stop()

# تحميل بيانات الشقق
apartments_file = "Cleaned_airbnb_v1.xlsx"
df_apartments = pd.read_excel(apartments_file, sheet_name='Sheet1')
df_apartments = df_apartments[['room_id', 'name', 'price_per_month', 'rating', 'latitude', 'longitude', 'URL']]


arabic_mapping = {
    "bus_stops":         "مواقف الحافلات",
    "groceries":         "محلات البقالة",
    "gyms":              "صالات رياضية",
    "hospitals_clinics": "مستشفيات وعيادات",
    "pharmacies":        "صيدليات",
    "restaurants":       "مطاعم",
    "cafes_bakeries":    "المقاهي والمخابز",
    "entertainment":     "أماكن الترفيه",
    "malls":             "مراكز تجارية",
    "metro_stations":    "محطات المترو"
}


# Suppose your DataFrame is called `places_df` and has a column "Category"
places_df["Category"] = places_df["Category"].replace(arabic_mapping)



# 4) Sidebar: Inputs & Selections
with st.sidebar:
    st.image('logo.png', width=400)  # Adjust width to make the logo size appropriate

    st.markdown("<h2 style='color: brown;'>خيارات البحث 🔍</h2>", unsafe_allow_html=True)
    st.write("<span style='color: #6B4F31;'>اِختـر فِئـاتَـك المفضّلـة عند السكن *من هنــا* ⬇️</span>", unsafe_allow_html=True)
    
    # Radius selection using a slider
    radius_km = st.slider("اختر نصف القطر (كم):", min_value=0.5, max_value=15.0, value=5.0, step=0.5)
    
    # Allow the user to select service categories
    st.subheader("اختر نوع الخدمة (يمكن اختيار أكثر من نوع):")
    categories = sorted(places_df["Category"].unique())
    selected_services_ar = st.session_state["selected_categories"] = st.multiselect("اختر نوع الخدمة:", categories)

    places_df_v2['Category_Arabic'] = places_df_v2['Category'].map(arabic_mapping)
    service_types = places_df_v2['Category_Arabic'].dropna().unique().tolist()

    # تحويل الاختيارات العربية إلى الأصلية لاستخدامها في التصفية
    selected_services = [key for key, value in arabic_mapping.items() if value in selected_services_ar]


def main():
    st.title("خريطة تفاعلية للخدمات (ألوان وأيقونات مميزة)")


    # Define improved marker colors and icons for each category
    category_styles = {
    "مطاعم": {"color": "red", "icon": "utensils"},
    "المقاهي والمخابز": {"color": "orange", "icon": "coffee"},
    "محلات البقالة": {"color": "green", "icon": "shopping-basket"},
    "أماكن الترفيه": {"color": "purple", "icon": "film"},
    "صالات رياضية": {"color": "darkred", "icon": "dumbbell"},
    "مستشفيات وعيادات": {"color": "darkblue", "icon": "hospital"},
    "مراكز تجارية": {"color": "pink", "icon": "store"},
    "محطات المترو": {"color": "blue", "icon": "train"},
    "مواقف الحافلات": {"color": "cadetblue", "icon": "bus"},
    "صيدليات": {"color": "lightblue", "icon": "prescription-bottle-alt"}
}

    
    user_location = (24.7136, 46.6753) 


    # Initialize session state for clicked coordinates
    if "clicked_lat" not in st.session_state:
        st.session_state["clicked_lat"] = None
    if "clicked_lng" not in st.session_state:
        st.session_state["clicked_lng"] = None
    if "selected_categories" not in st.session_state:
        st.session_state["selected_categories"] = []

    # Create a map centered on Riyadh
    riyadh_center = [24.7136, 46.6753]
    m = folium.Map(location=riyadh_center, zoom_start=12)

    # Persisting the pin location
    if st.session_state["clicked_lat"] and st.session_state["clicked_lng"]:
        user_location = (st.session_state["clicked_lat"], st.session_state["clicked_lng"])
        m.location = user_location  # Ensuring the map stays on the last clicked location
        folium.Marker(
            location=user_location,
            popup="موقعك المختار",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
    else:
        user_location = riyadh_center
        
    # If user has clicked, drop pin and show available services
    if st.session_state["clicked_lat"] and st.session_state["clicked_lng"]:
        user_location = (st.session_state["clicked_lat"], st.session_state["clicked_lng"])

        # Add a circle and marker for the clicked location
        folium.Circle(
            location=user_location,
            radius=radius_km * 1000,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.2
        ).add_to(m)

        folium.Marker(
            location=user_location,
            popup=f"الإحداثيات المختارة\nنصف قطر البحث: {radius_km} كم",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)



        if st.session_state["selected_categories"]:
            # Calculate bounding box for filtering places
            lat_deg = radius_km / 111.0
            lon_deg = radius_km / (111.0 * math.cos(math.radians(user_location[0])))

            lat_min = user_location[0] - lat_deg
            lat_max = user_location[0] + lat_deg
            lon_min = user_location[1] - lon_deg
            lon_max = user_location[1] + lon_deg

            # Filter places within the bounding box
            mask_bbox = (
                (places_df["Latitude"] >= lat_min) &
                (places_df["Latitude"] <= lat_max) &
                (places_df["Longitude"] >= lon_min) &
                (places_df["Longitude"] <= lon_max)
            )
            places_in_bbox = places_df[mask_bbox]

            # Filter places by distance and category
            filtered_places = []
            for _, row in places_in_bbox.iterrows():
                place_location = (row["Latitude"], row["Longitude"])
                distance_km_calc = geodesic(user_location, place_location).km
                if distance_km_calc <= radius_km and row["Category"] in st.session_state["selected_categories"]:
                    row_dict = row.to_dict()
                    row_dict["Distance (km)"] = round(distance_km_calc, 2)
                    filtered_places.append(row_dict)

            # Add markers for filtered places with unique styles
            for place in filtered_places:
                category = place["Category"]
                style = category_styles.get(category, {"color": "gray", "icon": "map-marker"})

                popup_content = f"<b>{place['Name']}</b><br>التصنيف: {place['Category']}<br>التقييم: {place.get('Rating', 'غير متوفر')} ⭐<br>عدد التقييمات: {place.get('Number_of_Ratings', 'غير متوفر')}<br>المسافة: {place['Distance (km)']} كم"
                folium.Marker(
                    location=(place["Latitude"], place["Longitude"]),
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=popup_content,
                    icon=folium.Icon(color=style["color"], icon=style["icon"], prefix="fa")
                ).add_to(m)

    # Display the map and capture user clicks
    returned_data = st_folium(m, width=1000, height=1000, key="map")

    

    # Update session state with the clicked coordinates
    if returned_data and returned_data["last_clicked"] is not None:
        lat = returned_data["last_clicked"]["lat"]
        lon = returned_data["last_clicked"]["lng"]
        
        if 16 <= lat <= 32 and 34 <= lon <= 56:
            st.session_state["clicked_lat"] = lat
            st.session_state["clicked_lng"] = lon
        else:
            st.warning("يبدو أن الإحداثيات خارج حدود السعودية. انقر ضمن الخريطة في نطاق السعودية.")

    


    # 🔹 تحميل بيانات الصيدليات فقط
    df_pharmacies = places_df_v2[places_df_v2["Category"] == "pharmacies"]

    # 🔹 حساب المسافات للصيدليات
    filtered_pharmacies = []
    for _, row in df_pharmacies.iterrows():
        pharmacy_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, pharmacy_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_pharmacies.append(row_dict)

    filtered_pharmacies_df = pd.DataFrame(filtered_pharmacies)
    # 🔹 عرض إحصائيات الصيدليات فقط إذا تم اختيارها
    if "pharmacies" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🏥 عدد الصيدليات داخل {radius_km} كم: **{len(filtered_pharmacies_df)}**")

            if filtered_pharmacies_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي صيدليات داخل هذا النطاق!**  
                    💀 **إذا مفاصلك تعبانة أو تحتاج دواء يومي، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    فجأة يهجم عليك صداع، تدور بانادول… وما تلاقي إلا مشوار طويل بانتظارك! 🚗  
                    **تبي مغامرة يومية للبحث عن صيدلية؟ ولا تبي صيدلية جنب البقالة؟ القرار لك!** 🔥
                """, unsafe_allow_html=True)
            elif len(filtered_pharmacies_df) == 1:
                pharmacy = filtered_pharmacies_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد الصيدليات في هذا النطاق: 1 فقط!**  
                    📍 **الصيدلية الوحيدة هنا هي:** `{pharmacy['Name']}` وتبعد عنك **{pharmacy['المسافة (كم)']} كم!**  
                    💊 **إذا كنت شخص يعتمد على الأدوية اليومية أو عندك إصابات متكررة، فكر مرتين قبل تسكن هنا، لأن الصيدلية الوحيدة ممكن تكون مغلقة وقت الحاجة!** 😬
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    📊 **عدد الصيدليات داخل {radius_km} كم: {len(filtered_pharmacies_df)} 💊**  
                    👏 **تقدر تطمن!** لو احتجت بانادول في نص الليل، فيه خيارات متاحة لك 😉  
                    📍 **عندك عدة صيدليات حولك، وما يحتاج تطق مشوار طويل عشان تجيب دواء بسيط!** 🚗💨
                """, unsafe_allow_html=True)

                st.markdown("### 🏥 أقرب 3 صيدليات إليك:")
                closest_pharmacies = filtered_pharmacies_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_pharmacies.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع الصيدليات**
                if len(filtered_pharmacies_df) > 3:
                    with st.expander("🔍 عرض جميع الصيدليات"):
                        st.dataframe(filtered_pharmacies_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة
            st.image("Pharmacy.webp", use_container_width=True)

    if "metro_stations" in selected_services:
        # 🔹 تصفية محطات المترو داخل النطاق المحدد
        filtered_metro = []
        for _, row in places_df_v2[places_df_v2["Category"] == "metro_stations"].iterrows():
            metro_location = (row["Latitude"], row["Longitude"])
            distance = geodesic(user_location, metro_location).km
            if distance <= radius_km:
                row_dict = row.to_dict()
                row_dict["المسافة (كم)"] = round(distance, 2)
                filtered_metro.append(row_dict)

        # 🔹 تحويل القائمة إلى DataFrame
        filtered_metro_df = pd.DataFrame(filtered_metro)

        # 🔹 الآن يمكن استخدام `filtered_metro_df` بأمان
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### 🚉 عدد محطات المترو داخل {radius_km} كم: **{len(filtered_metro_df)}**")

            if filtered_metro_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي محطات مترو داخل هذا النطاق!**  
                    💀 **إذا كنت تعتمد على المترو يوميًا، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    فجأة تحتاج مشوار سريع، وتكتشف أنك عالق في الزحمة 🚗🚦  
                    **تبي تعيش بدون مترو؟ ولا تبي محطة جنب بيتك؟ القرار لك!** 🔥
                """, unsafe_allow_html=True)

            elif len(filtered_metro_df) == 1:
                metro = filtered_metro_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **هناك محطة مترو واحدة فقط في هذا النطاق!**  
                    📍 **المحطة الوحيدة هنا هي:** **\u202B{metro['Name']}\u202C** وتبعد عنك **{metro['المسافة (كم)']} كم**!  
                    🚆 **إذا كنت تعتمد على المترو يوميًا، فكر مرتين قبل السكن هنا، لأن المحطة الوحيدة قد تكون بعيدة عند الحاجة!** 😬
                """, unsafe_allow_html=True)


            else:
                st.markdown(f"""
                    📊 **عدد محطات المترو داخل {radius_km} كم: {len(filtered_metro_df)} 🚆**  
                    👏 **تقدر تطمن!** لو احتجت المترو في أي وقت، عندك خيارات متاحة لك 😉  
                    📍 **عندك عدة محطات مترو حولك، وما تحتاج تفكر في الزحمة!** 🚄💨
                """, unsafe_allow_html=True)

                st.markdown("### 🚉 أقرب 3 محطات مترو إليك:")
                closest_metro = filtered_metro_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_metro.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع محطات المترو**
                if len(filtered_metro_df) > 3:
                    with st.expander("🔍 عرض جميع محطات المترو"):
                        st.dataframe(filtered_metro_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل صورة لمحطات المترو
            st.image("Metro.webp", use_container_width=True)


    # 🔹 تحميل بيانات الأندية الرياضية فقط
    if "gyms" in selected_services:
        df_gyms = places_df_v2[places_df_v2["Category"] == "gyms"]

        # 🔹 حساب المسافات للأندية الرياضية
        filtered_gyms = []
        for _, row in df_gyms.iterrows():
            gym_location = (row["Latitude"], row["Longitude"])
            distance = geodesic(user_location, gym_location).km
            if distance <= radius_km:
                row_dict = row.to_dict()
                row_dict["المسافة (كم)"] = round(distance, 2)
                filtered_gyms.append(row_dict)

        filtered_gyms_df = pd.DataFrame(filtered_gyms)

        # 🔹 تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### 🏋️‍♂️ عدد الأندية الرياضية داخل {radius_km} كم: **{len(filtered_gyms_df)}**")

            if filtered_gyms_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي أندية رياضية داخل هذا النطاق!**  
                    💀 **إذا كنت ناوي تصير فتنس مود، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    بتضطر تتمرن في البيت مع فيديوهات يوتيوب، لأن النادي بعيد جدًا! 🚶‍♂️💨  
                    **تبي نادي قريب، ولا تكتفي بتمارين الضغط في الصالة؟ القرار لك!** 🔥
                """, unsafe_allow_html=True)

            elif len(filtered_gyms_df) == 1:
                gym = filtered_gyms_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد الأندية الرياضية في هذا النطاق: 1 فقط!**  
                    📍 **النادي الوحيد هنا هو:** `{gym['Name']}` وتبعد عنك **{gym['المسافة (كم)']} كم!**  
                    🏋️‍♂️ *يعني لو كان زحمة، ما عندك خيارات ثانية! لازم تستحمل الانتظار على الأجهزة الرياضية!* 😬  
                    **هل أنت مستعد لهذا التحدي؟**
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد الأندية الرياضية داخل {radius_km} كم: {len(filtered_gyms_df)} 🏋️‍♂️**  
                    👏 *هنيالك! عندك أكثر من خيار، وتقدر تختار النادي اللي يناسبك بدون عناء!* 😉  
                    📍 *ما يحتاج تتمرن في البيت، عندك أندية قريبة توفر لك كل شيء تحتاجه!* 💪🔥
                """, unsafe_allow_html=True)

                st.markdown("### 🏋️‍♂️ أقرب 3 أندية رياضية إليك:")
                closest_gyms = filtered_gyms_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_gyms.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع الأندية**
                if len(filtered_gyms_df) > 3:
                    with st.expander("🔍 عرض جميع الأندية"):
                        st.dataframe(filtered_gyms_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة
            st.image("GYM.webp", use_container_width=True)



    # 🔹 تصفية بيانات المستشفيات
    df_hospitals = places_df_v2[places_df_v2["Category"] == "hospitals_clinics"]

    # 🔹 حساب المسافات للمستشفيات
    filtered_hospitals = []
    for _, row in df_hospitals.iterrows():
        hospital_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, hospital_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_hospitals.append(row_dict)

    filtered_hospitals_df = pd.DataFrame(filtered_hospitals)
    # 🔹 عرض إحصائيات المستشفيات فقط إذا تم اختيارها
    if "hospitals_clinics" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🏥 عدد المستشفيات داخل {radius_km} كم: **{len(filtered_hospitals_df)}**")

            if filtered_hospitals_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي مستشفيات داخل هذا النطاق!**  
                    💀 **إذا كنت كثير الإصابات أو لديك مراجعات طبية متكررة، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    🚑 **ما فيه مستشفى قريب؟ يعني لو صادك مغص نص الليل، بتصير عندك مغامرة إسعافية مشوّقة!**  
                    **هل تحب تعيش بعيدًا عن المستشفيات، أم تفضل أن تكون قريبًا من الرعاية الصحية؟ القرار لك!** 🔥
                """, unsafe_allow_html=True)
            elif len(filtered_hospitals_df) == 1:
                hospital = filtered_hospitals_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد المستشفيات في هذا النطاق: 1 فقط!**  
                    📍 **المستشفى الوحيد هنا هو:** `{hospital['Name']}` وتبعد عنك **{hospital['المسافة (كم)']} كم!**  
                    🏥 **إذا كنت تحتاج إلى مستشفى قريب، هذا هو خيارك الوحيد! هل أنت مستعد لهذا التحدي؟** 🤔
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    📊 **عدد المستشفيات داخل {radius_km} كم: {len(filtered_hospitals_df)} 🏥🚑**  
                    👏 **إذا صار شيء، عندك خيارات كثيرة، وما تحتاج تسوي رحلة عبر القارات عشان توصل للطوارئ!** 😅  
                    📍 **المستشفيات قريبة منك، وصحتك في أمان!** 💉💊
                """, unsafe_allow_html=True)

                st.markdown("### 🏥 أقرب 3 مستشفيات إليك:")
                closest_hospitals = filtered_hospitals_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_hospitals.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع المستشفيات**
                if len(filtered_hospitals_df) > 3:
                    with st.expander("🔍 عرض جميع المستشفيات"):
                        st.dataframe(filtered_hospitals_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة
            st.image("Hospital.webp", use_container_width=True)
    # 🔹 تصفية بيانات المولات
    df_malls = places_df_v2[places_df_v2["Category"] == "malls"]

    # 🔹 حساب المسافات للمولات
    filtered_malls = []
    for _, row in df_malls.iterrows():
        mall_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, mall_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_malls.append(row_dict)

    filtered_malls_df = pd.DataFrame(filtered_malls)

    # 🔹 عرض إحصائيات المولات فقط إذا تم اختيارها
    if "malls" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🛍️ عدد المولات داخل {radius_km} كم: **{len(filtered_malls_df)}**")

            if filtered_malls_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي مولات داخل هذا النطاق!**  
                    💀 **إذا كنت من محبي التسوق، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    **ما فيه مول قريب؟ يعني لا مقاهي، لا براندات، لا تخفيضات فجائية؟ بتعيش حياة صعبة!** 🥲
                """, unsafe_allow_html=True)

            elif len(filtered_malls_df) == 1:
                mall = filtered_malls_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد المولات في هذا النطاق: 1 فقط!**  
                    📍 **المول الوحيد هنا هو:** `{mall['Name']}` وتبعد عنك **{mall['المسافة (كم)']} كم!**  
                    🛍️ **يعني لو كنت تدور على تنوع في المحلات، لا تتحمس… هذا هو خيارك الوحيد!** 😬  
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد المولات داخل {radius_km} كم: {len(filtered_malls_df)} 🛍️✨**  
                    👏 **هنيالك!** إذا طفشت، عندك خيارات كثيرة للشوبينغ، ما يحتاج تسافر بعيد عشان تشتري جزمة جديدة! 😉  
                    📍 **يعني بكل بساطة، خذ راحتك، وجرب أكثر من مول حسب مزاجك!** 💃🕺
                """, unsafe_allow_html=True)

                st.markdown("### 🛒 أقرب 3 مولات إليك:")
                closest_malls = filtered_malls_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_malls.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع المولات**
                if len(filtered_malls_df) > 3:
                    with st.expander("🔍 عرض جميع المولات"):
                        st.dataframe(filtered_malls_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة الخاصة بالمولات
            st.image("Mall.webp", use_container_width=True)

    # 🔹 تصفية بيانات محلات البقالة والسوبرماركت
    df_groceries = places_df_v2[places_df_v2["Category"] == "groceries"]

    # 🔹 حساب المسافات لمحلات السوبرماركت
    filtered_groceries = []
    for _, row in df_groceries.iterrows():
        grocery_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, grocery_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_groceries.append(row_dict)

    filtered_groceries_df = pd.DataFrame(filtered_groceries)

    # 🔹 عرض إحصائيات السوبرماركت فقط إذا تم اختيارها
    if "groceries" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🛒 عدد محلات البقالة داخل {radius_km} كم: **{len(filtered_groceries_df)}**")

            if filtered_groceries_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي محلات بقالة أو سوبرماركت داخل هذا النطاق!**  
                    💀 **إذا كنت من النوع اللي يشتري أكل بيومه، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    **يعني إذا خلصت البيض فجأة؟ لازم مشوار عشان تجيب كرتون جديد!** 🥚🚗
                """, unsafe_allow_html=True)

            elif len(filtered_groceries_df) == 1:
                grocery = filtered_groceries_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد محلات البقالة في هذا النطاق: 1 فقط!**  
                    📍 **المحل الوحيد هنا هو:** `{grocery['Name']}` وتبعد عنك **{grocery['المسافة (كم)']} كم!**  
                    🛒 **يعني إذا كان زحمة، أو سكّر بدري، فأنت في ورطة! جهّز نفسك لطلب التوصيل أو خزن الأكل مسبقًا!** 😬  
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد محلات البقالة داخل {radius_km} كم: {len(filtered_groceries_df)} 🛒🥦**  
                    👏 **ما يحتاج تشيل هم الأكل، عندك محلات كثيرة تقدر تشتري منها أي وقت!** 😉  
                    📍 **لو نسيت تشتري خبز، ما يحتاج مشوار طويل، أقرب بقالة عندك!** 🍞🥛
                """, unsafe_allow_html=True)

                st.markdown("### 🛒 أقرب 3 محلات بقالة إليك:")
                closest_groceries = filtered_groceries_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_groceries.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع محلات البقالة**
                if len(filtered_groceries_df) > 3:
                    with st.expander("🔍 عرض جميع محلات البقالة"):
                        st.dataframe(filtered_groceries_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة الخاصة بالسوبرماركت
            st.image("supermarket.webp", use_container_width=True)

    # 🔹 تصفية بيانات أماكن الترفيه
    df_entertainment = places_df_v2[places_df_v2["Category"] == "entertainment"]

    # 🔹 حساب المسافات لأماكن الترفيه
    filtered_entertainment = []
    for _, row in df_entertainment.iterrows():
        entertainment_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, entertainment_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_entertainment.append(row_dict)

    filtered_entertainment_df = pd.DataFrame(filtered_entertainment)

    # 🔹 عرض إحصائيات أماكن الترفيه فقط إذا تم اختيارها
    if "entertainment" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🎭 عدد أماكن الترفيه داخل {radius_km} كم: **{len(filtered_entertainment_df)}**")

            if filtered_entertainment_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي أماكن ترفيه داخل هذا النطاق!**  
                    💀 **إذا كنت تحب الطلعات والأماكن الحماسية، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    **يعني لا سينما، لا ملاهي، لا جلسات حلوة؟! الحياة بتكون مملة جدًا! 😭**
                """, unsafe_allow_html=True)

            elif len(filtered_entertainment_df) == 1:
                entertainment = filtered_entertainment_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد أماكن الترفيه في هذا النطاق: 1 فقط!**  
                    📍 **المكان الوحيد هنا هو:** `{entertainment['Name']}` وتبعد عنك **{entertainment['المسافة (كم)']} كم!**  
                    🎢 **يعني لو طفشت، عندك خيار واحد فقط! تحب تكرر نفس المشوار؟ ولا تفضل يكون عندك تنوع؟** 🤔
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد أماكن الترفيه داخل {radius_km} كم: {len(filtered_entertainment_df)} 🎢🎭**  
                    👏 **يا حظك! عندك أماكن كثيرة للترفيه، يعني ما فيه ملل أبد!** 😍  
                    📍 **إذا كنت تحب السينما، الألعاب، أو الجلسات الممتعة، تقدر تخطط لطلعات بدون تفكير!** 🍿🎮
                """, unsafe_allow_html=True)

                st.markdown("### 🎭 أقرب 3 أماكن ترفيه إليك:")
                closest_entertainment = filtered_entertainment_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_entertainment.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع أماكن الترفيه**
                if len(filtered_entertainment_df) > 3:
                    with st.expander("🔍 عرض جميع أماكن الترفيه"):
                        st.dataframe(filtered_entertainment_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة الخاصة بأماكن الترفيه
            st.image("Event.webp", use_container_width=True)

    # 🔹 تصفية بيانات المقاهي والمخابز
    df_cafes_bakeries = places_df_v2[places_df_v2["Category"] == "cafes_bakeries"]

    # 🔹 حساب المسافات للمقاهي والمخابز
    filtered_cafes_bakeries = []
    for _, row in df_cafes_bakeries.iterrows():
        cafe_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, cafe_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_cafes_bakeries.append(row_dict)

    filtered_cafes_bakeries_df = pd.DataFrame(filtered_cafes_bakeries)

    # 🔹 عرض إحصائيات المقاهي والمخابز فقط إذا تم اختيارها
    if "cafes_bakeries" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### ☕ عدد المقاهي والمخابز داخل {radius_km} كم: **{len(filtered_cafes_bakeries_df)}**")

            if filtered_cafes_bakeries_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي مقاهي أو مخابز داخل هذا النطاق!**  
                    💀 **إذا كنت من مدمني القهوة أو عاشق الدونات، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    **يعني لا كابتشينو صباحي؟ لا كرواسون طازج؟ بتعيش حياة جافة جدًا! 😭☕🥐**
                """, unsafe_allow_html=True)

            elif len(filtered_cafes_bakeries_df) == 1:
                cafe = filtered_cafes_bakeries_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد المقاهي والمخابز في هذا النطاق: 1 فقط!**  
                    📍 **المكان الوحيد هنا هو:** `{cafe['Name']}` وتبعد عنك **{cafe['المسافة (كم)']} كم!**  
                    ☕ **يعني لو طفشت من نفس المقهى، ما عندك غيره! تحب تكرر نفس القهوة كل يوم؟ ولا تفضّل تنوع؟** 🤔
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد المقاهي والمخابز داخل {radius_km} كم: {len(filtered_cafes_bakeries_df)} ☕🍩**  
                    👏 **أنت في نعيم! عندك مقاهي ومخابز كثيرة، يعني صباحاتك بتكون مثالية وكل يوم تجرب شيء جديد!** 😍  
                    📍 **سواء تحب اللاتيه، الإسبريسو، أو الدونات، الخيارات عندك كثيرة!** 🥐☕
                """, unsafe_allow_html=True)

                st.markdown("### 🍩 أقرب 3 مقاهي ومخابز إليك:")
                closest_cafes_bakeries = filtered_cafes_bakeries_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_cafes_bakeries.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع المقاهي والمخابز**
                if len(filtered_cafes_bakeries_df) > 3:
                    with st.expander("🔍 عرض جميع المقاهي والمخابز"):
                        st.dataframe(filtered_cafes_bakeries_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة الخاصة بالمقاهي والمخابز
            st.image("Cafe.webp", use_container_width=True)

    # 🔹 تصفية بيانات المطاعم
    df_restaurants = places_df_v2[places_df_v2["Category"] == "restaurants"]

    # 🔹 حساب المسافات للمطاعم
    filtered_restaurants = []
    for _, row in df_restaurants.iterrows():
        restaurant_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, restaurant_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_restaurants.append(row_dict)

    filtered_restaurants_df = pd.DataFrame(filtered_restaurants)

    # 🔹 عرض إحصائيات المطاعم فقط إذا تم اختيارها
    if "restaurants" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🍽️ عدد المطاعم داخل {radius_km} كم: **{len(filtered_restaurants_df)}**")

            if filtered_restaurants_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي مطاعم داخل هذا النطاق!**  
                    💀 **إذا كنت تعتمد على المطاعم وما تطبخ، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    **يعني لا برجر، لا بيتزا، لا شاورما؟ بتعيش على النودلز والبيض المقلي؟ 🥲🍳**
                """, unsafe_allow_html=True)

            elif len(filtered_restaurants_df) == 1:
                restaurant = filtered_restaurants_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد المطاعم في هذا النطاق: 1 فقط!**  
                    📍 **المطعم الوحيد هنا هو:** `{restaurant['Name']}` وتبعد عنك **{restaurant['المسافة (كم)']} كم!**  
                    🍽️ **يعني لو ما عجبك، مالك إلا تطبخ بنفسك! تبي تعيش على منيو محدود؟ ولا تفضل يكون عندك تنوع؟** 🤔
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد المطاعم داخل {radius_km} كم: {len(filtered_restaurants_df)} 🍔🍕**  
                    👏 **هنيالك! عندك مطاعم كثيرة، يعني خياراتك مفتوحة سواء تبغى شاورما، سوشي، ولا مندي!** 😍  
                    📍 **كل يوم تقدر تجرب مطعم جديد، وما فيه ملل أبد!** 🍛🍣
                """, unsafe_allow_html=True)

                st.markdown("### 🍔 أقرب 3 مطاعم إليك:")
                closest_restaurants = filtered_restaurants_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_restaurants.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع المطاعم**
                if len(filtered_restaurants_df) > 3:
                    with st.expander("🔍 عرض جميع المطاعم"):
                        st.dataframe(filtered_restaurants_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة الخاصة بالمطاعم
            st.image("restaurant.webp", use_container_width=True)
    # 🔹 تصفية بيانات محطات الباص
    df_bus_stations = places_df_v2[places_df_v2["Category"] == "bus_stops"]

    # 🔹 حساب المسافات لمحطات الباص
    filtered_bus_stations = []
    for _, row in df_bus_stations.iterrows():
        bus_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(user_location, bus_location).km
        if distance <= radius_km:
            row_dict = row.to_dict()
            row_dict["المسافة (كم)"] = round(distance, 2)
            filtered_bus_stations.append(row_dict)

    filtered_bus_stations_df = pd.DataFrame(filtered_bus_stations)

    # 🔹 عرض إحصائيات محطات الباص فقط إذا تم اختيارها
    if "bus_stops" in selected_services:
        # تقسيم الصفحة إلى عمودين: النص في اليسار والصورة في اليمين
        col1, col2 = st.columns([3, 1])  # العمود الأول أكبر ليحتوي على النص

        with col1:
            st.markdown(f"### 🚌 عدد محطات الباص داخل {radius_km} كم: **{len(filtered_bus_stations_df)}**")

            if filtered_bus_stations_df.empty:
                st.markdown("""
                    🚨 **لا توجد أي محطات باص داخل هذا النطاق!**  
                    💀 **إذا كنت تعتمد على الباصات في تنقلاتك، فكر مليون مرة قبل تسكن هنا!** 😵‍💫  
                    **يعني لازم تمشي مشوار محترم عشان تلقى محطة؟ بتصير خبير في المشي بالغصب! 🚶‍♂️😂**
                """, unsafe_allow_html=True)

            elif len(filtered_bus_stations_df) == 1:
                bus_station = filtered_bus_stations_df.iloc[0]
                st.markdown(f"""
                    ⚠️ **عدد محطات الباص في هذا النطاق: 1 فقط!**  
                    📍 **المحطة الوحيدة هنا هي:** `{bus_station['Name']}` وتبعد عنك **{bus_station['المسافة (كم)']} كم!**  
                    🚌 *🚏 يعني لو فاتك الباص، لا تشيل هم، بعد ٦ دقايق بيجيك الثاني! بس المشكلة؟ إذا كانت المحطة بعيدة، بتتمشى مشوار محترم كل مرة! 😬 تبي تعتمد على محطة وحدة؟ ولا تفضل يكون عندك خيارات أقرب؟* 🤔
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                    📊 **عدد محطات الباص داخل {radius_km} كم: {len(filtered_bus_stations_df)} 🚌🚏**  
                    👏 **يا سلام! عندك محطات باص كثيرة، تنقلاتك صارت سهلة وما تحتاج تنتظر طويل!** 😍  
                    📍 **ما تحتاج تمشي كثير، أقرب محطة جنبك، ومستعد تنطلق لمشاويرك!** 🚍💨
                """, unsafe_allow_html=True)

                st.markdown("### 🚏 أقرب 3 محطات باص إليك:")
                closest_bus_stations = filtered_bus_stations_df.nsmallest(3, "المسافة (كم)")
                for _, row in closest_bus_stations.iterrows():
                    st.markdown(f"🔹 **{row['Name']}** - تبعد {row['المسافة (كم)']} كم")

                # 🔹 **إضافة زر لعرض جميع محطات الباص**
                if len(filtered_bus_stations_df) > 3:
                    with st.expander("🔍 عرض جميع محطات الباص"):
                        st.dataframe(filtered_bus_stations_df[['Name', 'المسافة (كم)']], use_container_width=True)

        with col2:
            # تحميل الصورة الخاصة بمحطات الباص
            st.image("bus.webp", use_container_width=True)

    # تصفية الشقق بناءً على الموقع المختار
    if st.session_state["clicked_lat"] and st.session_state["clicked_lng"]:
        user_location = (st.session_state["clicked_lat"], st.session_state["clicked_lng"])
        
        # إنشاء KDTree لتسريع البحث
        apartments_tree = cKDTree(df_apartments[["latitude", "longitude"]].values)
        radius_in_degrees = radius_km / 111
        
        nearest_indices = apartments_tree.query_ball_point([user_location], r=radius_in_degrees)[0]
        nearby_apartments = df_apartments.iloc[nearest_indices].drop_duplicates(subset=["room_id"])

        if not nearby_apartments.empty:
            st.write("### 🏠 الشقق القريبة من الموقع المختار")
            st.dataframe(nearby_apartments[['name', 'price_per_month', 'rating', 'URL']], use_container_width=True)

            # تعريف خريطة Folium جديدة مع التركيز على الموقع المختار
            m_apartments = folium.Map(location=user_location, zoom_start=14, tiles='cartodb positron')

            # وضع علامة للموقع المختار
            folium.Marker(
                location=user_location,
                icon=folium.Icon(color='red', icon='map-marker', prefix='fa'),
                tooltip='موقعك المختار'
            ).add_to(m_apartments)

            # إضافة الشقق إلى الخريطة
            for idx, row in nearby_apartments.iterrows():
                popup_html = f"""
                <b>{row['name']}</b><br>
                السعر: {row['price_per_month']}<br>
                التقييم: {row['rating']} ⭐<br>
                <a href="{row['URL']}" target="_blank">رابط الشقة</a>
                """
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=7,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.9,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=row['name']
                ).add_to(m_apartments)

            # عرض الخريطة النهائية للشقق
            st_folium(m_apartments, width=1000, height=1000)
            
        else:
            st.warning("لم يتم العثور على شقق بالقرب من الموقع المختار. جرب توسيع نطاق البحث.")

if __name__ == "__main__":
    main()
