#!/bin/bash
# Helper script for managing DashBorges Docker operations

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

case "$1" in
    start)
        echo -e "${GREEN}Starting DashBorges containers...${NC}"
        docker-compose up -d
        echo -e "${GREEN}DashBorges is running!${NC}"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "API: http://localhost:8000"
        ;;
    stop)
        echo -e "${YELLOW}Stopping DashBorges containers...${NC}"
        docker-compose down
        echo -e "${GREEN}DashBorges stopped.${NC}"
        ;;
    restart)
        echo -e "${YELLOW}Restarting DashBorges containers...${NC}"
        docker-compose restart
        echo -e "${GREEN}DashBorges restarted!${NC}"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "API: http://localhost:8000"
        ;;
    logs)
        echo -e "${GREEN}Showing DashBorges logs:${NC}"
        docker-compose logs -f
        ;;
    rebuild)
        echo -e "${YELLOW}Rebuilding DashBorges containers...${NC}"
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "${GREEN}DashBorges rebuilt and running!${NC}"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "API: http://localhost:8000"
        ;;
    backup)
        # Create a backup of the data volume
        BACKUP_FILE="dashborges_backup_$(date +'%Y%m%d_%H%M%S').tar"
        echo -e "${GREEN}Creating backup of DashBorges data...${NC}"
        docker run --rm -v dashborges_data:/data -v $(pwd):/backup alpine tar -cf /backup/$BACKUP_FILE -C /data .
        echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Please provide a backup file to restore from.${NC}"
            echo -e "Usage: $0 restore <backup_file>"
            exit 1
        fi
        if [ ! -f "$2" ]; then
            echo -e "${YELLOW}Backup file not found: $2${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Restoring DashBorges data from $2...${NC}"
        docker-compose down
        docker run --rm -v dashborges_data:/data -v $(pwd):/backup alpine sh -c "rm -rf /data/* && tar -xf /backup/$(basename $2) -C /data"
        docker-compose up -d
        echo -e "${GREEN}Data restored successfully!${NC}"
        ;;
    *)
        echo -e "DashBorges Docker Management Script"
        echo -e "---------------------------------"
        echo -e "Usage: $0 {start|stop|restart|logs|rebuild|backup|restore <backup_file>}"
        echo -e ""
        echo -e "Commands:"
        echo -e "  start         Start DashBorges containers"
        echo -e "  stop          Stop DashBorges containers"
        echo -e "  restart       Restart DashBorges containers"
        echo -e "  logs          Show live logs"
        echo -e "  rebuild       Rebuild containers from scratch"
        echo -e "  backup        Create a backup of the data volume"
        echo -e "  restore       Restore from a backup file"
        exit 1
        ;;
esac

exit 0
