<?php
require_once (WCF_DIR . 'lib/data/DatabaseObjectList.class.php');
require_once (CP_DIR . 'lib/data/email/Email.class.php');

/**
 * Handels a list of emails
 *
 * @author		Tobias Friebel
 * @copyright	2009 Tobias Friebel
 * @license		GNU General Public License <http://opensource.org/licenses/gpl-2.0.php>
 * @package		com.toby.cp.email
 * @subpackage	data.email
 * @category 	Control Panel
 */
class EmailList extends DatabaseObjectList
{
	public $emails = array ();

	/**
	 * @see DatabaseObjectList::countObjects()
	 */
	public function countObjects()
	{
		$sql = "SELECT	COUNT(*) AS count
				FROM	cp" . CP_N . "_mail_virtual
			" . (!empty($this->sqlConditions) ? "WHERE " . $this->sqlConditions : '');
		$row = WCF :: getDB()->getFirstRow($sql);
		return $row['count'];
	}

	/**
	 * @see DatabaseObjectList::readObjects()
	 */
	public function readObjects()
	{
		// die selects nicht tauschen, sonst haben emails ohne account keine adresse mehr...
		$sql = "SELECT		" . (!empty($this->sqlSelects) ? $this->sqlSelects . ',' : '') . "
							account.*, virtual.*
				FROM		cp" . CP_N . "_mail_virtual virtual
				LEFT JOIN	cp" . CP_N . "_mail_account account USING (accountID) 
				" . $this->sqlJoins . "
				" . (!empty($this->sqlConditions) ? "WHERE " . $this->sqlConditions : '') . "
				" . (!empty($this->sqlOrderBy) ? "ORDER BY " . $this->sqlOrderBy : '');
		
		$result = WCF :: getDB()->sendQuery($sql, $this->sqlLimit, $this->sqlOffset);
		
		while ($row = WCF :: getDB()->fetchArray($result))
		{
			$this->emails[] = new Email(null, $row);
		}
	}

	/**
	 * @see DatabaseObjectList::getObjects()
	 */
	public function getObjects()
	{
		return $this->emails;
	}
}
?>