import streamlit as st
import database as db
import utils
from datetime import datetime
import plotly.graph_objects as go

# Set page config at the very beginning
st.set_page_config(
    page_title="ROI Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database
db.init_db()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def login_page():
    st.title("Impact Calculator Login")
    
    role = st.selectbox("Select your role", ["Customer", "Project Manager", "IT Director"])
    
    if role == "Customer":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                user = db.verify_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.page = 'customer_dashboard'
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
        
        with col2:
            if st.button("Create Account"):
                st.session_state.page = 'register'
                st.experimental_rerun()
    else:
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if password == "Vbhjyjdf4?1":
                st.session_state.user = {'role': role.lower()}
                if role == "Project Manager":
                    st.session_state.page = 'project_manager_dashboard'
                elif role == "IT Director":
                    st.session_state.page = 'it_director_dashboard'
                st.experimental_rerun()
            else:
                st.error("Invalid password")

def register_page():
    st.title("Create Customer Account")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password == confirm_password:
            if db.create_user(username, password, "customer"):
                st.success("Account created successfully! Please login.")
                st.session_state.page = 'login'
                st.experimental_rerun()
            else:
                st.error("Username already exists")
        else:
            st.error("Passwords do not match")

def customer_dashboard():
    st.markdown("""
        <div class="section-header">Customer Dashboard</div>
    """, unsafe_allow_html=True)
    
    # Create new project
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Create New Project</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Project Title")
            project_type = st.selectbox(
                "Project Type",
                options=["New Development", "Enhancement", "Maintenance", "Support"]
            )
            description = st.text_area("Project Description")
        
        with col2:
            core_functionality = st.text_area("Core Functionality")
            expected_revenue = st.number_input(
                "Expected Revenue ($)", 
                min_value=0.0,
                value=0.0,
                step=1000.0,
                help="Enter the expected revenue in dollars"
            )
            time_savings = st.number_input(
                "Time Savings (hours/month)", 
                min_value=0.0,
                value=0.0,
                step=10.0,
                help="Enter the expected time savings in hours per month"
            )
            efficiency_improvement = st.slider(
                "Efficiency Improvement (%)", 
                0, 100, 0,
                help="Enter the expected efficiency improvement as a percentage"
            )
            comments = st.text_area("Comments")
        
        # Descartes Square Section
        st.markdown("""
            <div class="section-header">Descartes Square Analysis</div>
            <div class="metric-card">
                <div class="metric-label">Please fill in the Descartes Square to help evaluate the project impact</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">What will happen if we do this?</div>
                </div>
            """, unsafe_allow_html=True)
            positive_consequences = st.text_area(
                "Positive consequences of implementing the project",
                help="List all the positive outcomes and benefits that will occur if the project is implemented"
            )
            
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">What won't happen if we do this?</div>
                </div>
            """, unsafe_allow_html=True)
            negative_consequences = st.text_area(
                "Negative consequences of implementing the project",
                help="List all the potential negative outcomes or risks that might occur if the project is implemented"
            )
        
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">What will happen if we don't do this?</div>
                </div>
            """, unsafe_allow_html=True)
            missed_opportunities = st.text_area(
                "Missed opportunities if we don't implement the project",
                help="List all the opportunities and benefits we might miss if we don't implement the project"
            )
            
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">What won't happen if we don't do this?</div>
                </div>
            """, unsafe_allow_html=True)
            avoided_risks = st.text_area(
                "Risks we avoid by not implementing the project",
                help="List all the risks and negative outcomes we avoid by not implementing the project"
            )
        
        submitted = st.form_submit_button("Create Project")
        
        if submitted:
            if not title:
                st.error("Please enter a project title")
            else:
                project_id = db.create_project(title, description, project_type, st.session_state.user[0])
                if project_id:
                    db.save_project_inputs(project_id, {
                        'expected_revenue': expected_revenue,
                        'time_savings': time_savings,
                        'efficiency_improvement': efficiency_improvement,
                        'customer_comments': comments,
                        'core_functionality': core_functionality,
                        'descartes_square': {
                            'positive_consequences': positive_consequences,
                            'negative_consequences': negative_consequences,
                            'missed_opportunities': missed_opportunities,
                            'avoided_risks': avoided_risks
                        }
                    })
                    st.success("Project created successfully!")
                else:
                    st.error("Failed to create project")
    
    # List existing projects
    st.markdown("""
        <div class="section-header">Your Projects</div>
    """, unsafe_allow_html=True)
    
    projects = db.get_user_projects(st.session_state.user[0])
    for project in projects:
        with st.expander(f"{project[1]} - {project[4]} ({project[3]})"):
            inputs = db.get_project_inputs(project[0])
            if not inputs:
                inputs = {}
            
            # Display project details
            st.write(f"**Description:** {project[2]}")
            st.write(f"**Core Functionality:** {inputs.get('core_functionality', 'Not specified')}")
            st.write(f"**Status:** {project[4]}")
            
            # Benefits
            st.subheader("Benefits")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"Expected Revenue: ${float(inputs.get('expected_revenue', 0)):,.2f}")
            with col2:
                st.write(f"Time Savings: {float(inputs.get('time_savings', 0)):.1f} hours/month")
            with col3:
                st.write(f"Efficiency Improvement: {float(inputs.get('efficiency_improvement', 0)):.1f}%")
            
            if inputs.get('customer_comments'):
                st.subheader("Comments")
                st.write(inputs['customer_comments'])
            
            if project[6]:  # PM estimate
                st.write(f"PM Estimate: ${float(project[6]):,.2f}")
            if project[7]:  # IT Director estimate
                st.write(f"IT Director Estimate: ${float(project[7]):,.2f}")

def pm_dashboard():
    st.markdown("""
        <div class="section-header">Project Manager Dashboard</div>
    """, unsafe_allow_html=True)
    
    # Get all projects
    projects = db.get_all_projects()
    
    if not projects:
        st.warning("No projects found in the database")
        return
    
    # Project selection
    project_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in projects}
    selected_project = st.selectbox("Select Project", options=list(project_options.keys()))
    project_id = project_options[selected_project]
    
    # Get project data
    project_data = db.get_project(project_id)
    if not project_data:
        st.error("Unable to get project data.")
        return
    
    # Get existing inputs
    inputs = db.get_project_inputs(project_id)
    if not inputs:
        inputs = {}
    
    # Display project details
    st.subheader("Project Details")
    st.write(f"**Title:** {project_data[1]}")
    st.write(f"**Description:** {project_data[2]}")
    st.write(f"**Type:** {project_data[3]}")
    st.write(f"**Status:** {project_data[4]}")
    st.write(f"**Core Functionality:** {inputs.get('core_functionality', 'Not specified')}")
    
    # Edit form for project inputs
    with st.form(f"edit_inputs_{project_id}"):
        # Required IT roles
        st.subheader("1. Required IT Roles")
        st.write("Select the roles needed for the project and specify the required hours for each role.")
        
        it_roles = {
            "Business Analyst": "Gathers and analyzes business requirements",
            "Project Manager": "Manages project scope, timeline, and resources",
            "UI/UX Designer": "Designs user interface and experience",
            "Frontend Developer": "Develops client-side application",
            "Backend Developer": "Develops server-side application",
            "DevOps Engineer": "Manages deployment and infrastructure",
            "QA Engineer": "Tests and ensures quality",
            "Data Engineer": "Handles data processing and storage",
            "Security Engineer": "Ensures application security",
            "Technical Lead": "Provides technical guidance and architecture"
        }
        
        role_hours = {}
        for role, description in it_roles.items():
            with st.expander(f"{role} - {description}"):
                hours = st.number_input(f"Hours needed for {role}", 
                                      value=float(inputs.get('role_hours', {}).get(role, 0)),
                                      min_value=0.0,
                                      help=f"Specify how many hours the {role} needs to work on this project")
                role_hours[role] = hours
        
        # Project timeline
        st.subheader("2. Project Timeline")
        col1, col2 = st.columns(2)
        with col1:
            project_duration = st.number_input("Project Duration (months)", 
                                             value=float(inputs.get('project_duration', 1)),
                                             min_value=1.0,
                                             help="How long will the project take to complete?")
        with col2:
            maintenance_period = st.number_input("Maintenance Period (months)", 
                                               value=float(inputs.get('maintenance_period', 0)),
                                               min_value=0.0,
                                               help="How long will the project need maintenance support?")
        
        # Additional costs
        st.subheader("3. Additional Costs")
        col1, col2, col3 = st.columns(3)
        with col1:
            infrastructure_cost = st.number_input("Infrastructure Cost ($)", 
                                                value=float(inputs.get('infrastructure_cost', 0)),
                                                min_value=0.0,
                                                help="Cost of infrastructure (servers, cloud services, etc.)")
        with col2:
            software_licenses = st.number_input("Software Licenses ($)", 
                                              value=float(inputs.get('software_licenses', 0)),
                                              min_value=0.0,
                                              help="Cost of required software licenses")
        with col3:
            training_cost = st.number_input("Training Cost ($)", 
                                          value=float(inputs.get('training_cost', 0)),
                                          min_value=0.0,
                                          help="Cost of training users or staff")
        
        # PM Comments
        st.subheader("4. Project Manager Comments")
        pm_comments = st.text_area("Add your comments", 
                                 value=inputs.get('pm_comments', ''),
                                 help="Add any comments or notes about the project")
        
        if st.form_submit_button("Save Changes"):
            # Calculate total cost based on role hours (assuming average hourly rate of $100)
            total_hours = sum(float(hours) for hours in role_hours.values())
            labor_cost = total_hours * 100
            total_cost = labor_cost + infrastructure_cost + software_licenses + training_cost
            
            # Update project inputs
            inputs.update({
                'role_hours': role_hours,
                'project_duration': project_duration,
                'maintenance_period': maintenance_period,
                'infrastructure_cost': infrastructure_cost,
                'software_licenses': software_licenses,
                'training_cost': training_cost,
                'pm_comments': pm_comments,
                'total_cost': total_cost
            })
            
            db.save_project_inputs(project_id, inputs)
            db.update_project_status(project_id, 'estimated_by_pm')
            st.success("Project inputs updated successfully!")
            st.experimental_rerun()
    
    # Display current project status
    st.subheader("Current Project Status")
    status_colors = {
        'submitted': 'red',
        'estimated_by_pm': 'yellow',
        'approved_by_pm': 'green',
        'approved_by_it': 'blue'
    }
    status = project_data[4]
    st.markdown(f"**Status:** <span style='color: {status_colors.get(status, 'gray')}'>{status.replace('_', ' ').title()}</span>", unsafe_allow_html=True)
    
    # Display customer comments if any
    if inputs.get('customer_comments'):
        st.subheader("Customer Comments")
        st.write(inputs['customer_comments'])

def it_director_dashboard():
    st.markdown("""
        <div class="section-header">IT Director Dashboard</div>
    """, unsafe_allow_html=True)
    
    # Get all projects
    projects = db.get_all_projects()
    
    if not projects:
        st.warning("No projects found in the database")
        return
    
    # Project selection
    project_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in projects}
    selected_project = st.selectbox("Select Project", options=list(project_options.keys()))
    project_id = project_options[selected_project]
    
    # Get project data
    project_data = db.get_project(project_id)
    if not project_data:
        st.error("Unable to get project data.")
        return
    
    # Calculate ROI
    roi_data = calculate_roi(project_id)
    if not roi_data:
        st.error("Unable to calculate ROI for this project.")
        return
    
    # Display project details
    st.subheader("Project Details")
    st.write(f"**Title:** {project_data[1]}")
    st.write(f"**Description:** {project_data[2]}")
    st.write(f"**Type:** {project_data[3]}")
    st.write(f"**Status:** {project_data[4]}")
    
    # Get project inputs
    inputs = db.get_project_inputs(project_id)
    if inputs:
        st.write(f"**Core Functionality:** {inputs.get('core_functionality', 'Not specified')}")
        
        # Required roles
        st.subheader("Required IT Roles")
        role_hours = inputs.get('role_hours', {})
        for role, hours in role_hours.items():
            if hours > 0:
                st.write(f"{role}: {hours:.1f} hours")
    
    # Create two columns for the layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Key Metrics
        st.subheader("Key Metrics")
        st.metric("Total Benefits", f"${roi_data['total_benefits']:,.2f}")
        st.metric("Total Costs", f"${roi_data['total_costs']:,.2f}")
        st.metric("ROI", f"{roi_data['roi']:.1f}%")
        
        # Project Status
        st.subheader("Project Status")
        status_colors = {
            'submitted': 'red',
            'estimated_by_pm': 'yellow',
            'approved_by_pm': 'green',
            'approved_by_it': 'blue'
        }
        status = project_data[4]
        st.markdown(f"**Status:** <span style='color: {status_colors.get(status, 'gray')}'>{status.replace('_', ' ').title()}</span>", unsafe_allow_html=True)
    
    with col2:
        # Benefits Breakdown
        st.subheader("Benefits Breakdown")
        benefits_data = {
            'Expected Revenue': roi_data['benefits_breakdown']['expected_revenue'],
            'Time Savings': roi_data['benefits_breakdown']['time_savings'],
            'Efficiency Improvement': roi_data['benefits_breakdown']['efficiency_improvement']
        }
        for benefit, value in benefits_data.items():
            if benefit == 'Efficiency Improvement':
                st.metric(benefit, f"{value:.1f}%")
            else:
                st.metric(benefit, f"${value:,.2f}")
        
        # Costs Breakdown
        st.subheader("Costs Breakdown")
        costs_data = {
            'Labor': roi_data['costs_breakdown']['labor'],
            'Infrastructure': roi_data['costs_breakdown']['infrastructure'],
            'Software': roi_data['costs_breakdown']['software'],
            'Training': roi_data['costs_breakdown']['training']
        }
        for cost, value in costs_data.items():
            st.metric(cost, f"${value:,.2f}")
    
    # Comments section
    st.subheader("Comments")
    
    # Display existing comments
    if inputs and inputs.get('customer_comments'):
        st.write("**Customer Comments:**")
        st.write(inputs['customer_comments'])
    
    if inputs and inputs.get('pm_comments'):
        st.write("**Project Manager Comments:**")
        st.write(inputs['pm_comments'])
    
    if inputs and inputs.get('it_comments'):
        st.write("**IT Director Comments:**")
        st.write(inputs['it_comments'])
    
    # Add IT Director comments
    with st.form("add_it_comment"):
        comment = st.text_area("Add your comment")
        if st.form_submit_button("Submit Comment"):
            if comment:
                inputs['it_comments'] = comment
                db.save_project_inputs(project_id, inputs)
                st.success("Comment added successfully!")
                st.experimental_rerun()
    
    # Approve button
    if project_data[4] != 'approved_by_it':
        if st.button("Approve Project", type="primary"):
            db.update_project_status(project_id, 'approved_by_it')
            st.success("Project approved successfully!")
            st.experimental_rerun()

def calculate_roi(project_id):
    try:
        # Get project data and inputs
        project_data = db.get_project(project_id)
        inputs = db.get_project_inputs(project_id)
        
        print(f"\n=== Calculating ROI for project {project_id} ===")
        print(f"Project data: {project_data}")
        print(f"Project inputs: {inputs}")
        
        # Calculate benefits
        expected_revenue = float(inputs.get('expected_revenue', 0))
        time_savings = float(inputs.get('time_savings', 0))
        efficiency_improvement_percent = float(inputs.get('efficiency_improvement', 0))
        
        # Convert efficiency improvement percentage to monetary value
        # Assuming efficiency improvement affects 20% of annual revenue
        project_duration = float(inputs.get('project_duration', 1))
        annual_revenue = expected_revenue / (project_duration / 12)
        efficiency_improvement = (annual_revenue * 0.2 * efficiency_improvement_percent / 100) * (project_duration / 12)
        
        print(f"Benefits calculation:")
        print(f"Expected Revenue: ${expected_revenue:,.2f}")
        print(f"Time Savings: ${time_savings:,.2f}")
        print(f"Efficiency Improvement: {efficiency_improvement_percent:.1f}% (${efficiency_improvement:,.2f})")
        
        # Calculate costs
        # Calculate labor costs based on role hours and rates
        role_hours = inputs.get('role_hours', {})
        total_labor_cost = 0
        
        # Standard hourly rates if not specified
        standard_rates = {
            'Business Analyst': 100,
            'Project Manager': 150,
            'UI/UX Designer': 120,
            'Frontend Developer': 120,
            'Backend Developer': 120,
            'DevOps Engineer': 130,
            'QA Engineer': 100,
            'Data Engineer': 130,
            'Security Engineer': 140,
            'Technical Lead': 160
        }
        
        for role, hours in role_hours.items():
            if hours > 0:
                rate = standard_rates.get(role, 120)  # Default rate if role not found
                total_labor_cost += float(hours) * rate
        
        # Additional costs
        infrastructure_cost = float(inputs.get('infrastructure_cost', 0))
        software_licenses = float(inputs.get('software_licenses', 0))
        training_cost = float(inputs.get('training_cost', 0))
        
        print(f"Costs calculation:")
        print(f"Labor Cost: ${total_labor_cost:,.2f}")
        print(f"Infrastructure: ${infrastructure_cost:,.2f}")
        print(f"Software: ${software_licenses:,.2f}")
        print(f"Training: ${training_cost:,.2f}")
        
        # Calculate total benefits and costs
        total_benefits = expected_revenue + time_savings + efficiency_improvement
        total_costs = total_labor_cost + infrastructure_cost + software_licenses + training_cost
        
        print(f"Total benefits: ${total_benefits:,.2f}")
        print(f"Total costs: ${total_costs:,.2f}")
        
        # Calculate ROI
        roi = ((total_benefits - total_costs) / total_costs * 100) if total_costs > 0 else 0
        print(f"ROI: {roi:.1f}%")
        
        # Update project inputs with calculated values
        inputs.update({
            'total_benefits': total_benefits,
            'total_costs': total_costs,
            'roi_percentage': roi,
            'labor_costs': total_labor_cost,
            'infrastructure_costs': infrastructure_cost,
            'software_costs': software_licenses,
            'training_costs': training_cost
        })
        
        # Save updated inputs
        db.save_project_inputs(project_id, inputs)
        
        return {
            'total_benefits': total_benefits,
            'total_costs': total_costs,
            'roi': roi,
            'benefits_breakdown': {
                'expected_revenue': expected_revenue,
                'time_savings': time_savings,
                'efficiency_improvement': efficiency_improvement_percent
            },
            'costs_breakdown': {
                'labor': total_labor_cost,
                'infrastructure': infrastructure_cost,
                'software': software_licenses,
                'training': training_cost
            }
        }
    except Exception as e:
        print(f"Error calculating ROI: {str(e)}")
        return {
            'total_benefits': 0,
            'total_costs': 0,
            'roi': 0,
            'benefits_breakdown': {
                'expected_revenue': 0,
                'time_savings': 0,
                'efficiency_improvement': 0
            },
            'costs_breakdown': {
                'labor': 0,
                'infrastructure': 0,
                'software': 0,
                'training': 0
            }
        }

def roi_calculator():
    st.markdown("""
        <div class="section-header">ROI Calculator</div>
    """, unsafe_allow_html=True)
    
    # Get all projects
    projects = db.get_all_projects()
    
    # Project selection
    project_titles = {p[0]: p[1] for p in projects}
    selected_project_id = st.selectbox(
        "Select Project",
        options=list(project_titles.keys()),
        format_func=lambda x: project_titles[x]
    )
    
    if selected_project_id:
        project = next(p for p in projects if p[0] == selected_project_id)
        inputs = db.get_project_inputs(selected_project_id)
        
        # Calculate ROI
        roi_data = calculate_roi(selected_project_id)
        
        # Project Overview Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Project Overview</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Project Title</div>
                    <div class="metric-value">{project[1]}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Project Type</div>
                    <div class="metric-value">{project[3]}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            status_class = f"status-{project[4]}"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Status</div>
                    <div class="status-badge {status_class}">{project[4].replace('_', ' ').title()}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Project Details Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Project Details</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div class="project-card">
                    <div class="project-card-title">Project Description</div>
                    <div class="project-card-content">{}</div>
                </div>
            """.format(project[2]), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="project-card">
                    <div class="project-card-title">Core Functionality</div>
                    <div class="project-card-content">{}</div>
                </div>
            """.format(inputs.get('core_functionality', 'Not specified')), unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Descartes Square Section
        if inputs.get('descartes_square'):
            st.markdown("""
                <div class="project-section">
                    <div class="section-header">Descartes Square Analysis</div>
                    <div class="descartes-square">
            """, unsafe_allow_html=True)
            
            # What will happen if we do this?
            st.markdown("""
                <div class="descartes-quadrant">
                    <div class="descartes-title">What will happen if we do this?</div>
                    <div class="descartes-content">{}</div>
                </div>
            """.format(inputs['descartes_square'].get('positive_consequences', 'Not specified')), unsafe_allow_html=True)
            
            # What won't happen if we do this?
            st.markdown("""
                <div class="descartes-quadrant">
                    <div class="descartes-title">What won't happen if we do this?</div>
                    <div class="descartes-content">{}</div>
                </div>
            """.format(inputs['descartes_square'].get('negative_consequences', 'Not specified')), unsafe_allow_html=True)
            
            # What will happen if we don't do this?
            st.markdown("""
                <div class="descartes-quadrant">
                    <div class="descartes-title">What will happen if we don't do this?</div>
                    <div class="descartes-content">{}</div>
                </div>
            """.format(inputs['descartes_square'].get('missed_opportunities', 'Not specified')), unsafe_allow_html=True)
            
            # What won't happen if we don't do this?
            st.markdown("""
                <div class="descartes-quadrant">
                    <div class="descartes-title">What won't happen if we don't do this?</div>
                    <div class="descartes-content">{}</div>
                </div>
            """.format(inputs['descartes_square'].get('avoided_risks', 'Not specified')), unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Benefits Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Project Benefits</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Expected Revenue</div>
                    <div class="metric-value">${roi_data['benefits_breakdown']['expected_revenue']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Time Savings</div>
                    <div class="metric-value">{roi_data['benefits_breakdown']['time_savings']:.1f} hours/month</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Efficiency Improvement</div>
                    <div class="metric-value">{roi_data['benefits_breakdown']['efficiency_improvement']:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Required IT Roles Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Required IT Roles</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        role_hours = inputs.get('role_hours', {})
        if role_hours:
            cols = st.columns(len(role_hours))
            for i, (role, hours) in enumerate(role_hours.items()):
                if hours > 0:  # Only show roles with hours
                    with cols[i]:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">{role}</div>
                                <div class="metric-value">{hours:.0f} hours</div>
                            </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Project Timeline Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Project Timeline</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Project Duration</div>
                    <div class="metric-value">{inputs.get('project_duration', 0):.0f} months</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Support Period</div>
                    <div class="metric-value">{inputs.get('maintenance_period', 0):.0f} months</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Project Costs Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Project Costs</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Labor Costs</div>
                    <div class="metric-value">${roi_data['costs_breakdown']['labor']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Infrastructure</div>
                    <div class="metric-value">${roi_data['costs_breakdown']['infrastructure']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Software</div>
                    <div class="metric-value">${roi_data['costs_breakdown']['software']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Training</div>
                    <div class="metric-value">${roi_data['costs_breakdown']['training']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # ROI Metrics Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">ROI Metrics</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Benefits</div>
                    <div class="metric-value">${roi_data['total_benefits']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Costs</div>
                    <div class="metric-value">${roi_data['total_costs']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">ROI</div>
                    <div class="metric-value">{roi_data['roi']:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Comments Section
        st.markdown("""
            <div class="project-section">
                <div class="section-header">Comments</div>
                <div class="project-grid">
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="comments-section">
                    <div class="comment-header">Customer Comments</div>
                    <div class="comment-content">{}</div>
                </div>
            """.format(inputs.get('customer_comments', 'No comments')), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="comments-section">
                    <div class="comment-header">PM Comments</div>
                    <div class="comment-content">{}</div>
                </div>
            """.format(inputs.get('pm_comments', 'No comments')), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="comments-section">
                    <div class="comment-header">IT Director Comments</div>
                    <div class="comment-content">{}</div>
                </div>
            """.format(inputs.get('it_comments', 'No comments')), unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def existing_projects():
    st.title("Existing Projects")
    
    # Get user's projects
    user_id = st.session_state.user[0] if isinstance(st.session_state.user, tuple) else st.session_state.user.get('id', 0)
    projects = db.get_projects_by_customer(user_id)
    
    if not projects:
        st.warning("No existing projects found.")
        return
    
    # Project selection
    project_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in projects}
    selected_project = st.selectbox("Select Project", options=list(project_options.keys()))
    project_id = project_options[selected_project]
    
    # Get project data
    project_data = db.get_project(project_id)
    if not project_data:
        st.error("Unable to get project data.")
        return
    
    # Get existing inputs
    existing_inputs = db.get_project_inputs(project_id)
    
    # Project details
    st.subheader("Project Details")
    st.write(f"**Title:** {project_data[1]}")
    st.write(f"**Status:** {project_data[4]}")
    
    # Input form
    st.subheader("Project Inputs")
    with st.form("existing_project_inputs"):
        # Benefits
        st.write("**Benefits**")
        expected_revenue = st.number_input("Expected Revenue ($)", 
                                         value=float(existing_inputs.get('expected_revenue', 0)),
                                         min_value=0.0)
        time_savings = st.number_input("Time Savings ($)", 
                                     value=float(existing_inputs.get('time_savings', 0)),
                                     min_value=0.0)
        efficiency_improvement = st.number_input("Efficiency Improvement ($)", 
                                               value=float(existing_inputs.get('efficiency_improvement', 0)),
                                               min_value=0.0)
        
        # Costs
        st.write("**Costs**")
        dev_hours = st.number_input("Development Hours", 
                                  value=float(existing_inputs.get('dev_hours', 0)),
                                  min_value=0.0)
        qa_hours = st.number_input("QA Hours", 
                                 value=float(existing_inputs.get('qa_hours', 0)),
                                 min_value=0.0)
        pm_hours = st.number_input("Project Management Hours", 
                                 value=float(existing_inputs.get('pm_hours', 0)),
                                 min_value=0.0)
        dev_rate = st.number_input("Development Rate ($/hour)", 
                                 value=float(existing_inputs.get('dev_rate', 0)),
                                 min_value=0.0)
        qa_rate = st.number_input("QA Rate ($/hour)", 
                                value=float(existing_inputs.get('qa_rate', 0)),
                                min_value=0.0)
        pm_rate = st.number_input("PM Rate ($/hour)", 
                                value=float(existing_inputs.get('pm_rate', 0)),
                                min_value=0.0)
        infrastructure_cost = st.number_input("Infrastructure Cost ($)", 
                                            value=float(existing_inputs.get('infrastructure_cost', 0)),
                                            min_value=0.0)
        software_licenses = st.number_input("Software Licenses ($)", 
                                          value=float(existing_inputs.get('software_licenses', 0)),
                                          min_value=0.0)
        training_cost = st.number_input("Training Cost ($)", 
                                      value=float(existing_inputs.get('training_cost', 0)),
                                      min_value=0.0)
        
        # Timeline
        st.write("**Timeline**")
        project_duration = st.number_input("Project Duration (months)", 
                                         value=float(existing_inputs.get('project_duration', 1)),
                                         min_value=1.0)
        maintenance_period = st.number_input("Maintenance Period (months)", 
                                           value=float(existing_inputs.get('maintenance_period', 0)),
                                           min_value=0.0)
        
        submitted = st.form_submit_button("Save Inputs")
        
        if submitted:
            # Save inputs
            inputs = {
                'expected_revenue': expected_revenue,
                'time_savings': time_savings,
                'efficiency_improvement': efficiency_improvement,
                'dev_hours': dev_hours,
                'qa_hours': qa_hours,
                'pm_hours': pm_hours,
                'dev_rate': dev_rate,
                'qa_rate': qa_rate,
                'pm_rate': pm_rate,
                'infrastructure_cost': infrastructure_cost,
                'software_licenses': software_licenses,
                'training_cost': training_cost,
                'project_duration': project_duration,
                'maintenance_period': maintenance_period
            }
            
            db.save_project_inputs(project_id, inputs)
            st.success("Project inputs saved successfully!")
            st.experimental_rerun()

def enhancements():
    st.title("Enhancements")
    
    # Get user's projects
    user_id = st.session_state.user[0] if isinstance(st.session_state.user, tuple) else st.session_state.user.get('id', 0)
    projects = db.get_projects_by_customer(user_id)
    
    if not projects:
        st.warning("No projects found to enhance.")
        return
    
    # Project selection
    project_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in projects}
    selected_project = st.selectbox("Select Project to Enhance", options=list(project_options.keys()))
    project_id = project_options[selected_project]
    
    # Get project data
    project_data = db.get_project(project_id)
    if not project_data:
        st.error("Unable to get project data.")
        return
    
    # Get existing inputs
    existing_inputs = db.get_project_inputs(project_id)
    
    # Project details
    st.subheader("Project Details")
    st.write(f"**Title:** {project_data[1]}")
    st.write(f"**Status:** {project_data[4]}")
    
    # Input form
    st.subheader("Enhancement Inputs")
    with st.form("enhancement_inputs"):
        # Benefits
        st.write("**Benefits**")
        expected_revenue = st.number_input("Expected Revenue ($)", 
                                         value=float(existing_inputs.get('expected_revenue', 0)),
                                         min_value=0.0)
        time_savings = st.number_input("Time Savings ($)", 
                                     value=float(existing_inputs.get('time_savings', 0)),
                                     min_value=0.0)
        efficiency_improvement = st.number_input("Efficiency Improvement ($)", 
                                               value=float(existing_inputs.get('efficiency_improvement', 0)),
                                               min_value=0.0)
        
        # Costs
        st.write("**Costs**")
        dev_hours = st.number_input("Development Hours", 
                                  value=float(existing_inputs.get('dev_hours', 0)),
                                  min_value=0.0)
        qa_hours = st.number_input("QA Hours", 
                                 value=float(existing_inputs.get('qa_hours', 0)),
                                 min_value=0.0)
        pm_hours = st.number_input("Project Management Hours", 
                                 value=float(existing_inputs.get('pm_hours', 0)),
                                 min_value=0.0)
        dev_rate = st.number_input("Development Rate ($/hour)", 
                                 value=float(existing_inputs.get('dev_rate', 0)),
                                 min_value=0.0)
        qa_rate = st.number_input("QA Rate ($/hour)", 
                                value=float(existing_inputs.get('qa_rate', 0)),
                                min_value=0.0)
        pm_rate = st.number_input("PM Rate ($/hour)", 
                                value=float(existing_inputs.get('pm_rate', 0)),
                                min_value=0.0)
        infrastructure_cost = st.number_input("Infrastructure Cost ($)", 
                                            value=float(existing_inputs.get('infrastructure_cost', 0)),
                                            min_value=0.0)
        software_licenses = st.number_input("Software Licenses ($)", 
                                          value=float(existing_inputs.get('software_licenses', 0)),
                                          min_value=0.0)
        training_cost = st.number_input("Training Cost ($)", 
                                      value=float(existing_inputs.get('training_cost', 0)),
                                      min_value=0.0)
        
        # Timeline
        st.write("**Timeline**")
        project_duration = st.number_input("Project Duration (months)", 
                                         value=float(existing_inputs.get('project_duration', 1)),
                                         min_value=1.0)
        maintenance_period = st.number_input("Maintenance Period (months)", 
                                           value=float(existing_inputs.get('maintenance_period', 0)),
                                           min_value=0.0)
        
        submitted = st.form_submit_button("Save Enhancement Inputs")
        
        if submitted:
            # Save inputs
            inputs = {
                'expected_revenue': expected_revenue,
                'time_savings': time_savings,
                'efficiency_improvement': efficiency_improvement,
                'dev_hours': dev_hours,
                'qa_hours': qa_hours,
                'pm_hours': pm_hours,
                'dev_rate': dev_rate,
                'qa_rate': qa_rate,
                'pm_rate': pm_rate,
                'infrastructure_cost': infrastructure_cost,
                'software_licenses': software_licenses,
                'training_cost': training_cost,
                'project_duration': project_duration,
                'maintenance_period': maintenance_period
            }
            
            db.save_project_inputs(project_id, inputs)
            st.success("Enhancement inputs saved successfully!")
            st.experimental_rerun()

def main():
    # Light Theme
    st.markdown("""
        <style>
        :root {
            --primary-color: #2196F3;
            --secondary-color: #64B5F6;
            --accent-color: #90CAF9;
            --text-color: #333333;
            --light-gray: #F5F5F5;
            --border-color: #E0E0E0;
            --success-color: #4CAF50;
            --warning-color: #FFA726;
            --error-color: #F44336;
            --card-bg: #FFFFFF;
            --sidebar-bg: #FFFFFF;
            --input-bg: #FFFFFF;
            --hover-color: #F5F5F5;
            --descartes-bg: #FFFFFF;
            --descartes-border: #E0E0E0;
            --descartes-hover: #F8F9FA;
            --descartes-title: #2196F3;
            --descartes-text: #333333;
            --button-hover: #1976D2;
        }
        
        .stApp {
            background-color: var(--light-gray);
            color: var(--text-color);
        }
        
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: var(--button-hover);
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: white;
        }
        
        .stButton>button:focus {
            outline: none;
            box-shadow: 0 0 0 2px var(--accent-color);
        }
        
        .stButton>button:active {
            transform: translateY(0);
            box-shadow: none;
        }
        
        .stSelectbox>div>div>select {
            border-color: var(--border-color);
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        
        .stTextInput>div>div>input {
            border-color: var(--border-color);
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        
        .stNumberInput>div>div>input {
            border-color: var(--border-color);
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        
        .stTextArea>div>div>textarea {
            border-color: var(--border-color);
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        
        .stMarkdown h1 {
            color: var(--primary-color);
            font-weight: 600;
        }
        
        .stMarkdown h2 {
            color: var(--primary-color);
            font-weight: 500;
        }
        
        .stMarkdown h3 {
            color: var(--text-color);
            font-weight: 500;
        }
        
        .metric-card {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-color: var(--accent-color);
            background-color: var(--hover-color);
        }
        
        .metric-value {
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        .metric-label {
            color: var(--text-color);
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .section-header {
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--primary-color);
            font-size: 1.2rem;
        }
        
        .status-badge {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-submitted {
            background-color: var(--hover-color);
            color: var(--primary-color);
        }
        
        .status-estimated_by_pm {
            background-color: #FFF8E1;
            color: #F57F17;
        }
        
        .status-estimated_by_it {
            background-color: #FFF3E0;
            color: var(--warning-color);
        }
        
        .status-approved {
            background-color: #E8F5E9;
            color: var(--success-color);
        }
        
        .status-rejected {
            background-color: #FFEBEE;
            color: var(--error-color);
        }
        
        .project-section {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }
        
        .project-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .project-card {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        .project-card:hover {
            background-color: var(--hover-color);
            border-color: var(--accent-color);
        }
        
        .project-card-title {
            color: var(--primary-color);
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        
        .project-card-content {
            color: var(--text-color);
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .comments-section {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            margin-top: 1rem;
            border: 1px solid var(--border-color);
        }
        
        .comments-section:hover {
            background-color: var(--hover-color);
            border-color: var(--accent-color);
        }
        
        .comment-header {
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .comment-content {
            color: var(--text-color);
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .stSidebar {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }
        
        .stSidebar .sidebar-content {
            background-color: var(--sidebar-bg);
        }
        
        .stSidebar .sidebar-content .block-container {
            background-color: var(--sidebar-bg);
        }
        
        .stSidebar .sidebar-content .block-container .element-container {
            background-color: var(--sidebar-bg);
        }
        
        .stSidebar .sidebar-content .block-container .element-container .stMarkdown {
            background-color: var(--sidebar-bg);
        }
        
        .stSidebar .sidebar-content .block-container .element-container .stMarkdown h1 {
            color: var(--primary-color);
        }
        
        .stSidebar .sidebar-content .block-container .element-container .stButton>button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        .stSuccess {
            background-color: #E8F5E9;
            color: var(--success-color);
            border: 1px solid var(--success-color);
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .stError {
            background-color: #FFEBEE;
            color: var(--error-color);
            border: 1px solid var(--error-color);
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .stWarning {
            background-color: #FFF3E0;
            color: var(--warning-color);
            border: 1px solid var(--warning-color);
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Descartes Square styles */
        .descartes-square {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .descartes-quadrant {
            background-color: var(--descartes-bg);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--descartes-border);
            transition: all 0.2s ease;
        }
        
        .descartes-quadrant:hover {
            background-color: var(--descartes-hover);
            border-color: var(--accent-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .descartes-title {
            color: var(--descartes-title);
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--descartes-title);
        }
        
        .descartes-content {
            color: var(--descartes-text);
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        /* Additional styles for better contrast */
        .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {
            color: var(--text-color);
        }
        
        .stExpander {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .stExpander:hover {
            border-color: var(--accent-color);
            background-color: var(--hover-color);
        }
        
        .stExpander .streamlit-expanderHeader {
            color: var(--primary-color);
            font-weight: 500;
        }
        
        .stExpander .streamlit-expanderContent {
            background-color: var(--card-bg);
        }
        
        /* Form styles */
        .stForm {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        .stForm:hover {
            border-color: var(--accent-color);
            background-color: var(--hover-color);
        }
        
        /* Table styles */
        .stTable {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }
        
        .stTable th {
            background-color: var(--hover-color);
            color: var(--primary-color);
        }
        
        .stTable td {
            color: var(--text-color);
        }
        
        /* Slider styles */
        .stSlider .stSlider > div > div > div {
            background-color: var(--primary-color);
        }
        
        .stSlider .stSlider > div > div > div:hover {
            background-color: var(--secondary-color);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add logo and header
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <h1 style="margin: 0; color: var(--primary-color);">ROI Calculator</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    elif st.session_state.page == 'customer_dashboard':
        customer_dashboard()
    elif st.session_state.page == 'project_manager_dashboard':
        pm_dashboard()
    elif st.session_state.page == 'it_director_dashboard':
        it_director_dashboard()
    elif st.session_state.page == 'roi_calculator':
        roi_calculator()
    elif st.session_state.page == 'existing_projects':
        existing_projects()
    elif st.session_state.page == 'enhancements':
        enhancements()
    
    # Add navigation sidebar
    if st.session_state.page != 'login' and st.session_state.page != 'register':
        with st.sidebar:
            st.title("Navigation")
            if st.button("Logout"):
                st.session_state.clear()
                st.session_state.page = 'login'
                st.experimental_rerun()
            
            # Add ROI Calculator tab for all roles
            if st.button("ROI Calculator"):
                st.session_state.page = 'roi_calculator'
                st.experimental_rerun()
            
            # Role-specific navigation
            user_role = st.session_state.user[2] if isinstance(st.session_state.user, tuple) else st.session_state.user.get('role', '')
            if user_role == 'customer':
                if st.button("My Projects"):
                    st.session_state.page = 'customer_dashboard'
                    st.experimental_rerun()
            elif user_role == 'project manager':
                if st.button("Project Management"):
                    st.session_state.page = 'project_manager_dashboard'
                    st.experimental_rerun()
            elif user_role == 'it director':
                if st.button("IT Director Dashboard"):
                    st.session_state.page = 'it_director_dashboard'
                    st.experimental_rerun()

if __name__ == "__main__":
    main() 