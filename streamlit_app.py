import streamlit as st
import pandas as pd

def normalize_ivr_name(name):
    """Remove .five9ivr extension and normalize IVR name"""
    return name.replace('.five9ivr', '').strip()

def create_campaign_mapping(ivr_details_df):
    """Create mapping from IVR names to campaigns"""
    mapping = {}
    for _, row in ivr_details_df.iterrows():
        if pd.notna(row['IVR name']) and pd.notna(row['Associated campaign(s)']):
            base_name = normalize_ivr_name(row['IVR name'])
            mapping[base_name] = row['Associated campaign(s)']
            mapping[base_name + '.five9ivr'] = row['Associated campaign(s)']
    return mapping

def process_files(ivr_details_df, prompts_df):
    """Process the files and create the merged dataset"""
    # Create IVR to campaign mapping
    ivr_campaign_map = create_campaign_mapping(ivr_details_df)
    
    # Add campaign information to prompts
    results = []
    for _, row in prompts_df.iterrows():
        ivr_name = row['IVR Name']
        base_ivr_name = normalize_ivr_name(ivr_name)
        
        results.append({
            'IVR Name': ivr_name,
            'Prompt Name': row['Prompt Name'],
            'Associated Campaigns': ivr_campaign_map.get(ivr_name, '') or ivr_campaign_map.get(base_ivr_name, '')
        })
    
    return pd.DataFrame(results)

def main():
    st.set_page_config(page_title="IVR Prompt-Campaign Mapper", layout="wide")
    
    st.title("IVR Prompt-Campaign Mapper")
    st.markdown("""
    This app maps IVR prompts to their associated campaigns using two input files:
    1. IVR details CSV (containing IVR names and associated campaigns)
    2. Prompts CSV (containing IVR names and prompt names)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        ivr_details_file = st.file_uploader(
            "Upload IVR details CSV",
            type=['csv'],
            help="CSV file containing IVR names and associated campaigns"
        )
        
    with col2:
        prompts_file = st.file_uploader(
            "Upload prompts CSV",
            type=['csv'],
            help="CSV file containing IVR names and prompt names"
        )
    
    if ivr_details_file and prompts_file:
        try:
            # Read the files
            ivr_details_df = pd.read_csv(ivr_details_file)
            prompts_df = pd.read_csv(prompts_file)
            
            # Process files
            result_df = process_files(ivr_details_df, prompts_df)
            
            # Display statistics
            st.header("Results")
            col1, col2, col3 = st.columns(3)
            
            total_prompts = len(result_df)
            mapped_prompts = result_df['Associated Campaigns'].notna().sum()
            unmapped_prompts = total_prompts - mapped_prompts
            
            with col1:
                st.metric("Total Prompts", total_prompts)
            with col2:
                st.metric("Mapped Prompts", mapped_prompts)
            with col3:
                st.metric("Unmapped Prompts", unmapped_prompts)
            
            # Show the results
            st.subheader("Mapped Results")
            st.dataframe(result_df, use_container_width=True)
            
            # Download button
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download mapped results as CSV",
                data=csv,
                file_name="prompt_campaign_mapping.csv",
                mime="text/csv",
            )
            
            # Show unmapped IVRs if any exist
            if unmapped_prompts > 0:
                st.subheader("Unmapped IVRs")
                unmapped_ivrs = result_df[result_df['Associated Campaigns'] == '']['IVR Name'].unique()
                st.write("The following IVRs could not be matched to campaigns:")
                for ivr in unmapped_ivrs:
                    st.write(f"- {ivr}")
                
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")

if __name__ == "__main__":
    main()