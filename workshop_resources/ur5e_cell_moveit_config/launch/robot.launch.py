from os.path import join
import pprint
from launch import LaunchDescription
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import (
    generate_move_group_launch,
    generate_moveit_rviz_launch,
    generate_rsp_launch,
    generate_spawn_controllers_launch,
    generate_static_virtual_joint_tfs_launch,
    generate_warehouse_db_launch
)
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import UnlessCondition, IfCondition
from moveit_configs_utils.launch_utils import DeclareBooleanLaunchArg
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros_extras.actions import LoadMoveitConfig, GenerateMoveitLaunch, LoadYaml
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    
    database_config = DeclareBooleanLaunchArg(
            "db",
            default_value=False,
            description="By default, we do not start a database (it can be large)",
            )


    debug_config = DeclareBooleanLaunchArg(
            "debug",
            default_value=False,
            description="By default, we are not in debug mode",
        )
    
    rviz_config = DeclareBooleanLaunchArg(
            "use_rviz", 
            default_value=True,
            description="Whether to use RVIZ or not."    
        )
    
    robot_ip_config = DeclareLaunchArgument(
            name="robot_ip",
            default_value="192.168.56.2",
            description="The IP address of the robot to connect to."
        )
    
    load_moveit_config = LoadMoveitConfig(
        robot_name="ur5e_workcell_fake",
        package_name="ur5e_cell_moveit_config")
    
    generate_move_group_ld = GenerateMoveitLaunch(
        function=generate_move_group_launch
    )
    
    generate_moveit_rviz_ld = GenerateMoveitLaunch(
        function=generate_moveit_rviz_launch,
        condition=IfCondition(LaunchConfiguration("use_rviz"))
    )
    
    ur_control_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ur_robot_driver"), "launch", "ur_control.launch.py"])
        ),
        launch_arguments={
            "ur_type": "ur5e",              
            "use_fake_hardware": "false",
            "initial_joint_controller": "joint_trajectory_controller",
            "activate_joint_controller": "true",
            "robot_ip": "192.168.56.2",
            "description_package": "ur5e_cell_description",
            "description_file": "workcell.urdf.xacro",
            "launch_rviz": "false"
            }.items()
    )
    
    ld = LaunchDescription(
        [
            database_config,
            debug_config,
            rviz_config,
            robot_ip_config,
            load_moveit_config,
            ur_control_launch,
            generate_move_group_ld,
            generate_moveit_rviz_ld,
        ]
    )
    return ld