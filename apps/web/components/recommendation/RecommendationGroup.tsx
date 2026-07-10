"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { KnowledgeCommodityItem } from "@/types/api";
import { CommodityCard } from "./CommodityCard";
import type { RecommendationStatus } from "./RecommendationBadge";

interface RecommendationGroupProps {
  title: string;
  description: string;
  items: KnowledgeCommodityItem[];
  status: RecommendationStatus;
  accentColor: string;
  className?: string;
}

export function RecommendationGroup({
  title,
  description,
  items,
  status,
  accentColor,
  className,
}: RecommendationGroupProps) {
  if (items.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("space-y-2", className)}
    >
      <div
        className="flex items-center gap-3 p-3 rounded-[var(--radius-weather)] border"
        style={{
          backgroundColor: `${accentColor}08`,
          borderColor: `${accentColor}20`,
        }}
      >
        <div
          className="h-8 w-1 rounded-full shrink-0"
          style={{ backgroundColor: accentColor }}
        />
        <div>
          <h4
            className="text-[12px] font-semibold"
            style={{ color: accentColor }}
          >
            {title}
          </h4>
          <p className="text-[9px] text-[var(--text-muted)] mt-0.5">
            {description}
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item, i) => (
          <CommodityCard key={item.komoditas_id} item={item} status={status} index={i} />
        ))}
      </div>
    </motion.div>
  );
}
