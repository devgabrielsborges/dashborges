#!/bin/bash
# Helper script for managing DashBorges Docker operations

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Function to show volume information
show_volumes() {
    echo -e "${GREEN}DashBorges Data Volumes:${NC}"
    echo -e "Data Volume: $(docker volume inspect dashborges_dashborges_data --format '{{.Mountpoint}}' 2>/dev/null || echo 'Not found')"
    echo -e "Config Volume: $(docker volume inspect dashborges_dashborges_config --format '{{.Mountpoint}}' 2>/dev/null || echo 'Not found')"
    echo -e "Logs Volume: $(docker volume inspect dashborges_dashborges_logs --format '{{.Mountpoint}}' 2>/dev/null || echo 'Not found')"
}

case "$1" in
    start)
        check_docker
        echo -e "${GREEN}Starting DashBorges containers...${NC}"
        docker-compose up -d
        echo -e "${GREEN}DashBorges is running!${NC}"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "API: http://localhost:8000"
        show_volumes
        ;;
    stop)
        check_docker
        echo -e "${YELLOW}Stopping DashBorges containers...${NC}"
        docker-compose down
        echo -e "${GREEN}DashBorges stopped.${NC}"
        ;;
    restart)
        check_docker
        echo -e "${YELLOW}Restarting DashBorges containers...${NC}"
        docker-compose restart
        echo -e "${GREEN}DashBorges restarted!${NC}"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "API: http://localhost:8000"
        ;;
    logs)
        check_docker
        echo -e "${GREEN}Showing DashBorges logs:${NC}"
        docker-compose logs -f
        ;;
    rebuild)
        check_docker
        echo -e "${YELLOW}Rebuilding DashBorges containers...${NC}"
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "${GREEN}DashBorges rebuilt and running!${NC}"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "API: http://localhost:8000"
        show_volumes
        ;;
    backup)
        check_docker
        # Create a comprehensive backup of all data volumes
        BACKUP_DIR="./backups"
        TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
        BACKUP_FILE="dashborges_full_backup_${TIMESTAMP}.tar.gz"
        
        mkdir -p "$BACKUP_DIR"
        
        echo -e "${GREEN}Creating comprehensive backup of DashBorges data...${NC}"
        
        # Backup all three volumes
        docker run --rm \
            -v dashborges_dashborges_data:/data \
            -v dashborges_dashborges_config:/config \
            -v dashborges_dashborges_logs:/logs \
            -v $(pwd)/$BACKUP_DIR:/backup \
            alpine tar -czf /backup/$BACKUP_FILE -C / data config logs
        
        echo -e "${GREEN}Comprehensive backup created: $BACKUP_DIR/$BACKUP_FILE${NC}"
        echo -e "Backup includes: database, configuration, and log files"
        ;;
    restore)
        check_docker
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Please provide a backup file to restore from.${NC}"
            echo -e "Usage: $0 restore <backup_file>"
            exit 1
        fi
        if [ ! -f "$2" ]; then
            echo -e "${RED}Backup file not found: $2${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Restoring DashBorges data from $2...${NC}"
        echo -e "${RED}Warning: This will overwrite all existing data!${NC}"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down
            docker run --rm \
                -v dashborges_dashborges_data:/data \
                -v dashborges_dashborges_config:/config \
                -v dashborges_dashborges_logs:/logs \
                -v $(pwd):$(dirname $2) \
                alpine sh -c "rm -rf /data/* /config/* /logs/* && tar -xzf $2 -C /"
            docker-compose up -d
            echo -e "${GREEN}Data restored successfully!${NC}"
        else
            echo -e "${YELLOW}Restore cancelled.${NC}"
        fi
        ;;
    volumes)
        check_docker
        echo -e "${GREEN}DashBorges Volume Information:${NC}"
        show_volumes
        echo ""
        echo -e "${GREEN}Volume Usage:${NC}"
        docker system df -v | grep dashborges || echo "No DashBorges volumes found"
        ;;
    clean)
        check_docker
        echo -e "${YELLOW}This will remove all DashBorges containers and volumes!${NC}"
        echo -e "${RED}Warning: All data will be permanently lost!${NC}"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -f
            echo -e "${GREEN}DashBorges cleaned up successfully.${NC}"
        else
            echo -e "${YELLOW}Cleanup cancelled.${NC}"
        fi
        ;;
    *)
        echo -e "DashBorges Docker Management Script"
        echo -e "---------------------------------"
        echo -e "Usage: $0 {start|stop|restart|logs|rebuild|backup|restore|volumes|clean}"
        echo -e ""
        echo -e "Commands:"
        echo -e "  start         Start DashBorges containers"
        echo -e "  stop          Stop DashBorges containers"
        echo -e "  restart       Restart DashBorges containers"
        echo -e "  logs          Show live logs"
        echo -e "  rebuild       Rebuild containers from scratch"
        echo -e "  backup        Create a comprehensive backup of all data"
        echo -e "  restore       Restore from a backup file"
        echo -e "  volumes       Show volume information and usage"
        echo -e "  clean         Remove all containers and volumes (DESTRUCTIVE)"
        exit 1
        ;;
esac

exit 0